#!/usr/bin/env python
# encoding: utf-8
#
# Copyright  (c) 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-02-24
#

"""Drives Script Filter to show unit conversions in Alfred 3."""

from __future__ import print_function

import os
import sys

from pint import UnitRegistry, UndefinedUnitError, DimensionalityError

from workflow import Workflow3, ICON_WARNING, ICON_INFO
from workflow.background import run_in_background, is_running
from config import (
    bootstrap,
    DEFAULT_UNIT_DEFINITIONS,
    BUILTIN_UNIT_DEFINITIONS,
    COPY_UNIT,
    CURRENCY_CACHE_AGE,
    CURRENCY_CACHE_NAME,
    CUSTOM_DEFINITIONS_FILENAME,
    DECIMAL_PLACES,
    DECIMAL_SEPARATOR,
    DEFAULT_SETTINGS,
    HELP_URL,
    ICON_UPDATE,
    THOUSANDS_SEPARATOR,
    UPDATE_SETTINGS,
)
from defaults import Defaults

log = None

# Pint objects
ureg = None
# Q = ureg.Quantity


class NoToUnits(Exception):
    """Raised if there are no to units (or defaults)."""


class Input(object):
    """Parsed user query."""

    def __init__(self, number, dimensionality, from_unit, to_unit=None):
        self.number = number
        self.dimensionality = dimensionality
        self.from_unit = from_unit
        self.to_unit = to_unit

    def __repr__(self):
        return ('Input(number={!r}, dimensionality={!r}, '
                'from_unit={!r}, to_unit={!r})').format(
                    self.number,
                    self.dimensionality, self.from_unit, self.to_unit)

    def __str__(self):
        return self.__repr__()


class Formatter(object):
    """Format a number."""

    def __init__(self, decimal_places=2, decimal_separator='.',
                 thousands_separator=''):
        self.decimal_places = decimal_places
        self.decimal_separator = decimal_separator
        self.thousands_separator = thousands_separator

    def formatted(self, n, unit=None):
        sep = u''
        if self.thousands_separator:
            sep = u','

        fmt = u'{{:0{}.{:d}f}}'.format(sep, self.decimal_places)
        num = fmt.format(n)
        # log.debug('n=%r, fmt=%r, num=%r', n, fmt, num)
        num = num.replace(',', '||comma||')
        num = num.replace('.', '||point||')
        num = num.replace('||comma||', self.thousands_separator)
        num = num.replace('||point||', self.decimal_separator)

        if unit:
            num = u'{} {}'.format(num, unit)

        return num


class Conversion(object):
    """Results of a conversion.

    Attributes:
        dimensionality (str): Dimensionality of conversion
        from_number (float): Input
        from_unit (str): Unit of input
        to_number (float): Conversion result
        to_unit (str): Unit of output

    """

    def __init__(self, from_number, from_unit, to_number, to_unit,
                 dimensionality):
        self.from_number = from_number
        self.from_unit = from_unit
        self.to_number = to_number
        self.to_unit = to_unit
        self.dimensionality = dimensionality

    def __str__(self):
        return u'{:f} {} = {:f} {} {}'.format(
            self.from_number, self.from_unit, self.to_number, self.to_unit,
            self.dimensionality).encode('utf-8')

    def __repr__(self):
        return ('Conversion(from_number={!r}, from_unit={!r}, '
                'to_number={!r}, to_unit={!r}, dimensionality={!r}').format(
                    self.from_number, self.from_unit, self.to_number,
                    self.to_unit, self.dimensionality)


class Converter(object):
    """Parse query and convert.

    Attributes:
        defaults (defaults.Defaults): Default units for conversions.

    """

    def __init__(self, defaults):
        """Create new `Converter`.

        Args:
            defaults (defaults.Defaults): Default units for conversions.

        """
        self.defaults = defaults

    def convert(self, i):
        """Convert ``Input``."""
        if i.to_unit is not None:
            units = [i.to_unit]
        else:
            units = [u for u in self.defaults.defaults(i.dimensionality)
                     if u != i.from_unit]

        if not units:
            raise NoToUnits()

        results = []
        qty = ureg.Quantity(i.number, i.from_unit)
        for u in units:
            to_unit = ureg.Quantity(1, u)
            conv = qty.to(to_unit)
            log.debug('%s -> %s = %s', i.from_unit, u, conv)
            results.append(Conversion(i.number, i.from_unit,
                                      conv.magnitude, u, i.dimensionality))

        return results

    def parse(self, query):
        """Parse user query into `Input`."""
        # Parse number from start of query
        qty = []
        for c in query:
            if c in '1234567890.,':
                qty.append(c)
            else:
                break
        if not len(qty):
            raise ValueError('Start your query with a number')

        tail = query[len(qty):].strip()
        qty = float(''.join(qty))

        if not len(tail):
            raise ValueError('No units specified')

        log.debug('quantity : %s tail : %s', qty, tail)

        # Try to parse rest of query into a pair of units
        from_unit = to_unit = None
        units = [s.strip() for s in tail.split()]
        from_unit = units[0]
        if len(units) > 1:
            to_unit = units[1]
        if len(units) > 2:
            raise ValueError('More than 2 units specified')

        try:
            from_unit = ureg.Quantity(qty, from_unit)
        except UndefinedUnitError:
            raise ValueError('Unknown unit: ' + from_unit)

        if to_unit:
            try:
                to_unit = ureg.Quantity(1, to_unit)
            except UndefinedUnitError:
                raise ValueError('Unknown unit: ' + to_unit)

        tu = None
        if to_unit:
            tu = unicode(to_unit.units)
        i = Input(from_unit.magnitude, unicode(from_unit.dimensionality),
                  unicode(from_unit.units), tu)

        log.debug(i)

        return i


def format_number(n):
    """Format a floating point number with thousands/decimal separators.

    Args:
        n (float): Number to format

    """
    sep = ''
    if THOUSANDS_SEPARATOR:
        sep = ','

    fmt = '{{:0{}.{:d}f}}'.format(sep, DECIMAL_PLACES)
    num = fmt.format(n)
    # log.debug('n=%r, fmt=%r, num=%r', n, fmt, num)
    num = num.replace(',', '||comma||')
    num = num.replace('.', '||point||')
    num = num.replace('||comma||', THOUSANDS_SEPARATOR)
    num = num.replace('||point||', DECIMAL_SEPARATOR)
    return num


def register_units():
    """Add built-in and user units to unit registry."""
    # Add custom units from workflow and user data
    ureg.load_definitions(BUILTIN_UNIT_DEFINITIONS)

    user_definitions = wf.datafile(CUSTOM_DEFINITIONS_FILENAME)

    # User's custom units
    if os.path.exists(user_definitions):
        ureg.load_definitions(user_definitions)


def register_exchange_rates(exchange_rates):
    """Add currency definitions with exchange rates to unit registry.

    Args:
        exchange_rates (dict): `{symbol: rate}` mapping of currencies.

    """
    # EUR will be the baseline currency. All exchange rates are
    # defined relative to the euro
    ureg.define('EUR = [currency] = eur')

    for abbr, rate in exchange_rates.items():
        definition = '{} = eur / {}'.format(abbr, rate)

        try:
            ureg.Quantity(1, abbr)
        except UndefinedUnitError:
            pass  # Unit does not exist
        else:
            log.debug('skipping currency %s : Unit is already defined', abbr)
            continue

        try:
            ureg.Quantity(1, abbr.lower())
        except UndefinedUnitError:
            definition += ' = {}'.format(abbr.lower())

        log.debug('registering currency : %r', definition)
        ureg.define(definition)


def convert(query):
    """Perform conversion and send results to Alfred."""
    error = None
    results = None

    defs = Defaults(wf)
    c = Converter(defs)

    try:
        i = c.parse(query)
    except ValueError as err:
        log.critical(u'invalid query (%s): %s', query, err)
        error = err.message

    else:
        try:
            results = c.convert(i)
            log.debug('results=%r', results)
        except NoToUnits:
            log.critical(u'No to_units (or defaults) for %s', i.dimensionality)
            error = u'No destination units (or defaults) for {}'.format(
                i.dimensionality)

        except DimensionalityError as err:
            log.critical(u'invalid conversion (%s): %s', query, err)
            error = u"Can't convert from {} {} to {} {}".format(
                err.units1, err.dim1, err.units2, err.dim2)

    if not error and not results:
        error = 'Conversion input not understood'

    if error:  # Show error
        wf.add_item(error,
                    'For example: 2.5cm in  |  178lb kg  |  200m/s mph',
                    valid=False, icon=ICON_WARNING)

    else:  # Show results
        f = Formatter(DECIMAL_PLACES, DECIMAL_SEPARATOR, THOUSANDS_SEPARATOR)
        wf.setvar('query', query)
        for conv in results:
            value = copytext = f.formatted(conv.to_number, conv.to_unit)
            if not COPY_UNIT:
                copytext = f.formatted(conv.to_number)

            it = wf.add_item(value,
                             valid=True,
                             arg=copytext,
                             copytext=copytext,
                             largetext=value,
                             icon='icon.png')

            action = 'save'
            name = 'Save'
            if defs.is_default(conv.dimensionality, conv.to_unit):
                action = 'delete'
                name = 'Remove'

            mod = it.add_modifier('cmd', u'{} {} as default unit for {}'.format(
                name, conv.to_unit, conv.dimensionality))
            mod.setvar('action', action)
            mod.setvar('unit', conv.to_unit)
            mod.setvar('dimensionality', conv.dimensionality)

    wf.send_feedback()
    log.debug('finished')
    return 0


def main(wf):
    """Run workflow Script Filter.

    Args:
        wf (workflow.Workflow): Current Workflow object.

    """
    global ureg
    ureg = UnitRegistry(wf.decode(DEFAULT_UNIT_DEFINITIONS))
    ureg.default_format = 'P'

    if not len(wf.args):
        return

    query = wf.args[0]  # .lower()
    log.debug('query : %s', query)

    # Create data files if necessary
    bootstrap(wf)

    # Add workflow and user units to unit registry
    register_units()

    # Notify of available update
    if wf.update_available:
        wf.add_item('A newer version is available',
                    'Action this item to download & install the new version',
                    autocomplete='workflow:update',
                    icon=ICON_UPDATE)

    # Load cached data
    exchange_rates = wf.cached_data(CURRENCY_CACHE_NAME, max_age=0)

    if exchange_rates:  # Add exchange rates to conversion database
        register_exchange_rates(exchange_rates)

    if not wf.cached_data_fresh(CURRENCY_CACHE_NAME, CURRENCY_CACHE_AGE):
        # Update currency rates
        cmd = ['/usr/bin/python', wf.workflowfile('currency.py')]
        run_in_background('update', cmd)
        wf.rerun = 0.5

    if is_running('update'):
        wf.rerun = 0.5
        if exchange_rates is None:  # No data cached yet
            wf.add_item(u'Fetching exchange rates…',
                        'Currency conversions will be momentarily possible',
                        icon=ICON_INFO)
        else:
            wf.add_item(u'Updating exchange rates…',
                        icon=ICON_INFO)

    return convert(query)


if __name__ == '__main__':
    wf = Workflow3(update_settings=UPDATE_SETTINGS,
                   default_settings=DEFAULT_SETTINGS,
                   help_url=HELP_URL)
    log = wf.logger
    sys.exit(wf.run(main))
