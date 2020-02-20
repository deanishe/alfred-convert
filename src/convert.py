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
from workflow.update import Version
from config import (
    bootstrap,
    DEFAULT_UNIT_DEFINITIONS,
    BUILTIN_UNIT_DEFINITIONS,
    COPY_UNIT,
    CURRENCY_CACHE_AGE,
    CURRENCY_CACHE_NAME,
    CURRENCY_DECIMAL_PLACES,
    CUSTOM_DEFINITIONS_FILENAME,
    DECIMAL_PLACES,
    DECIMAL_SEPARATOR,
    DEFAULT_SETTINGS,
    DYNAMIC_DECIMALS,
    HELP_URL,
    ICON_UPDATE,
    NOKEY_FILENAME,
    OPENX_APP_KEY,
    THOUSANDS_SEPARATOR,
    UPDATE_SETTINGS,
)
from defaults import Defaults

log = None

# Pint objects
ureg = None
# Q = ureg.Quantity


def unit_is_currency(unit):
    """Return ``True`` if specified unit is a fiat currency."""
    from config import CURRENCIES
    return unit.upper() in CURRENCIES


def open_currency_instructions():
    """Magic action to open help in browser."""
    import webbrowser
    webbrowser.open('https://github.com/deanishe/alfred-convert#conversions')
    return 'Opening instructions in browser...'


def error_if_currency(unit):
    """Show an error currency conversion isn't set up.

    Detect whether input is a currency, and show an error if it is and
    there's no API key for exchange rates.
    """
    if unit_is_currency(unit):
        log.error(
            "[parser] unit %s is a fiat currency, but OpenExchangeRates.org "
            "API key isn't set", unit)

        show_currency_help()
        sys.exit(0)


def show_currency_help():
    """Show a message in Alfred telling user to set ``APP_KEY``."""
    wf.add_item('Set APP_KEY to convert this currency',
                'Action this item for instructions',
                autocomplete='workflow:appkey',
                icon=ICON_WARNING)

    wf.send_feedback()


def handle_update(wf):
    """Clear cache on update.

    Delete cached data if last-run version used a different format,
    or if user has just added the ``APP_KEY`` for fiat currency
    exchange rates.

    """
    nokey = wf.cachefile(NOKEY_FILENAME)
    clear = False

    # Clear cache if previous version was old
    lv = wf.last_version_run
    log.debug('version=%s, last_version=%s', wf.version, lv)
    if wf.version > Version('3.0') and lv < Version('3.1'):
        log.debug('clearing cache: saved data is incompatible')
        clear = True

    if OPENX_APP_KEY:
        if os.path.exists(nokey):
            os.unlink(nokey)
            log.debug('clearing cache: APP_KEY was set')
            clear = True
    else:
        if not os.path.exists(nokey):
            open(nokey, 'wb').write('')

    if clear:
        wf.cache_data(CURRENCY_CACHE_NAME, None)
        log.debug('cleared old cached currencies')


class NoToUnits(Exception):
    """Raised if there are no to units (or defaults)."""


class Input(object):
    """Parsed user query."""

    def __init__(self, number, dimensionality, from_unit,
                 to_unit=None, context=None):
        """Create new ``Input``."""
        self.number = number
        self.dimensionality = dimensionality
        self.from_unit = from_unit
        self.to_unit = to_unit
        self.context = context

    @property
    def is_currency(self):
        """`True` if Input is a currency."""
        return self.dimensionality == u'[currency]'

    def __repr__(self):
        """Code-like representation of `Input`."""
        return ('Input(number={!r}, dimensionality={!r}, '
                'from_unit={!r}, to_unit={!r})').format(
                    self.number, self.dimensionality, self.from_unit,
                    self.to_unit)

    def __str__(self):
        """Printable representation of `Input`."""
        return self.__repr__()


class Formatter(object):
    """Format a number.

    Attributes:
        decimal_places (int): Number of decimal places in formatted numbers
        decimal_separator (str): Character to use as decimal separator
        thousands_separator (str): Character to use as thousands separator

    """

    def __init__(self, decimal_places=2, decimal_separator='.',
                 thousands_separator='', dynamic_decimals=True):
        """Create a new `Formatter`."""
        self.decimal_places = decimal_places
        self.decimal_separator = decimal_separator
        self.thousands_separator = thousands_separator
        self.dynamic_decimals = dynamic_decimals

    def _decimal_places(self, n):
        """Calculate the number of decimal places the result should have.

        If :attr:`dynamic_decimals` is `True`, increase the number of
        decimal places until the result is non-zero.

        Args:
            n (float): Number that will be formatted.

        Returns:
            int: Number of decimal places for result.

        """
        log.debug('DYNAMIC_DECIMALS: %s', ('off', 'on')[self.dynamic_decimals])

        if not self.dynamic_decimals or n == 0.0:
            return self.decimal_places

        m = max(self.decimal_places, 10) + 1
        p = self.decimal_places
        while p < m:
            e = 10 ** p
            i = n * e
            # log.debug('n=%r, e=%d, i=%r, p=%d', n, e, i, p)
            if n * e >= 10:
                break

            p += 1

        # Remove trailing zeroes
        s = str(i)
        if '.' not in s:  # not a fraction
            return p

        _, s = s.split('.', 1)
        # log.debug('s=%s, p=%d', s, p)
        while s.endswith('0'):
            s = s[:-1]
            p -= 1
            # log.debug('s=%s, p=%d', s, p)

        p = max(p, self.decimal_places)
        log.debug('places=%d', p)
        return p

    def formatted(self, n, unit=None):
        """Format number with thousands and decimal separators."""
        sep = u''
        if self.thousands_separator:
            sep = u','

        fmt = u'{{:0{}.{:d}f}}'.format(sep, self._decimal_places(n))
        num = fmt.format(n)
        # log.debug('n=%r, fmt=%r, num=%r', n, fmt, num)
        num = num.replace(',', '||comma||')
        num = num.replace('.', '||point||')
        num = num.replace('||comma||', self.thousands_separator)
        num = num.replace('||point||', self.decimal_separator)

        if unit:
            num = u'{} {}'.format(num, unit)

        return num

    def formatted_no_thousands(self, n, unit=None):
        """Format number with decimal separator only."""
        fmt = u'{{:0.{:d}f}}'.format(self._decimal_places(n))
        num = fmt.format(n)
        # log.debug('n=%r, fmt=%r, num=%r', n, fmt, num)
        num = num.replace('.', '||point||')
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
        """Create a new `Conversion`."""
        self.from_number = from_number
        self.from_unit = from_unit
        self.to_number = to_number
        self.to_unit = to_unit
        self.dimensionality = dimensionality

    def __str__(self):
        """Pretty string representation."""
        return u'{:f} {} = {:f} {} {}'.format(
            self.from_number, self.from_unit, self.to_number, self.to_unit,
            self.dimensionality).encode('utf-8')

    def __repr__(self):
        """Code-like representation."""
        return ('Conversion(from_number={!r}, from_unit={!r}, '
                'to_number={!r}, to_unit={!r}, dimensionality={!r}').format(
                    self.from_number, self.from_unit, self.to_number,
                    self.to_unit, self.dimensionality)


class Converter(object):
    """Parse query and convert.

    Parses user input into an `Input` object, then converts this into
    one or more `Conversion` objects.

    Attributes:
        decimal_separator (str): Decimal separator character in input.
        defaults (defaults.Defaults): Default units for conversions.
        thousands_separator (str): Thousands separator character in input.

    """

    def __init__(self, defaults, decimal_separator='.',
                 thousands_separator=','):
        """Create new `Converter`.

        Args:
            defaults (defaults.Defaults): Default units for conversions.
            decimal_separator (str, optional): Decimal separator character
                in query.
            thousands_separator (str, optional): Thousands separator character
                in query.

        """
        self.defaults = defaults
        self.decimal_separator = decimal_separator
        self.thousands_separator = thousands_separator

    def convert(self, i):
        """Convert `Input`.

        Args:
            i (Input): Parsed user query

        Returns:
            list: Sequence of `Conversion` objects

        Raises:
            NoToUnits: Raised if user hasn't specified a destination unit
                or there are no default units for the given dimensionality
            ValueError: Raised if a unit is unknown

        """
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
            try:
                to_unit = ureg.Quantity(1, u)
            except UndefinedUnitError:
                error_if_currency(u)
                raise ValueError('Unknown unit: {}'.format(u))

            conv = qty.to(to_unit)
            log.debug('[convert] %s -> %s = %s', i.from_unit, u, conv)
            results.append(Conversion(i.number, i.from_unit,
                                      conv.magnitude, u, i.dimensionality))

        return results

    def parse(self, query):
        """Parse user query into `Input`.

        Args:
            query (str): User query

        Returns:
            Input: Parsed query

        Raises:
            ValueError: Raised if query is invalid

        """
        ctx, query = self.parse_context(query)
        qty, tail = self.parse_quantity(query)

        # Show error message for invalid input
        if qty is None:
            if ctx:
                raise ValueError('No quantity')

            raise ValueError('Start your query with a number')

        if not len(tail):
            raise ValueError('No units specified')

        log.debug('[parser] quantity=%s, tail=%s', qty, tail)

        # Parse query into pint.Quantity objects
        from_unit, to_unit = self.parse_units(tail, qty)

        # Create `Input` from parsed query
        tu = None
        if to_unit:
            tu = unicode(to_unit.units)
        i = Input(from_unit.magnitude, unicode(from_unit.dimensionality),
                  unicode(from_unit.units), tu, ctx)

        log.debug('[parser] %s', i)

        return i

    def parse_context(self, query):
        """Extract and set context.

        Args:
            query (str): User input

        Returns:
            (list/str, str): Parsed or empty context and rest of query

        Raises:
            ValueError: Raised if supplied context is invalid

        """
        ctx = []
        for c in query:
            if c in 'abcdefghijklmnopqrstuvwxyz':
                ctx.append(c)
            else:
                break

        if ctx:
            ctx = ''.join(ctx)
            try:
                ureg.enable_contexts(ctx)
            except KeyError:
                raise ValueError('Unknown context: {}'.format(ctx))

            log.debug('[parser] context=%s', ctx)
            query = query[len(ctx):].strip()

        return ctx, query

    def parse_quantity(self, query):
        """Extract quantity from query.

        Args:
            query (str): (Partial) user query

        Returns:
            (float, str): Quantity and remainder of query

        """
        qty = []
        qtychars = ('+-1234567890' + self.thousands_separator +
                    self.decimal_separator)
        for c in query:
            if c in qtychars:
                if c == '+':
                    qty.append('')
                if c == self.thousands_separator:
                    log.debug('ignored thousands separator "%s"', c)
                    # Append an empty string so qty length is correct
                    qty.append('')
                elif c == self.decimal_separator:
                    qty.append('.')
                else:
                    qty.append(c)
            else:
                break
        if not len(qty):
            return None, ''

        tail = query[len(qty):].strip()
        qty = float(''.join(qty))

        return qty, tail

    def parse_units(self, query, qty=1):
        """Extract from and (optional) to units from query.

        Args:
            query (str): (Partial) user input
            qty (int, optional): Quantity of from units

        Returns:
            (pint.Quantity, pint.Quantity): From and to quantities. To
                quantity is initialised with ``1``.

        Raises:
            ValueError: Raised if a unit is unknown, or more than 2 units
                are specified.

        """
        from_unit = to_unit = None
        units = [s.strip() for s in query.split()]
        from_unit = units[0]
        log.debug('[parser] from_unit=%s', from_unit)

        if len(units) > 1:
            to_unit = units[1]
            log.debug('[parser] to_unit=%s', to_unit)
        if len(units) > 2:
            raise ValueError('More than 2 units specified')

        # Validate units
        try:
            from_unit = ureg.Quantity(qty, from_unit)
        except UndefinedUnitError:
            error_if_currency(from_unit)
            raise ValueError('Unknown unit: ' + from_unit)

        if to_unit:
            try:
                to_unit = ureg.Quantity(1, to_unit)
            except UndefinedUnitError:
                error_if_currency(to_unit)
                raise ValueError('Unknown unit: ' + to_unit)

        return from_unit, to_unit


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
    # USD will be the baseline currency. All exchange rates are
    # defined relative to the US dollar
    ureg.define('USD = [currency] = usd')

    for abbr, rate in exchange_rates.items():
        definition = '{} = usd / {}'.format(abbr, rate)

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
    c = Converter(defs, DECIMAL_SEPARATOR, THOUSANDS_SEPARATOR)

    try:
        i = c.parse(query)
    except ValueError as err:
        log.critical(u'invalid query (%s): %s', query, err)
        error = err.message

    else:
        try:
            results = c.convert(i)
            # log.debug('results=%r', results)
        except NoToUnits:
            log.critical(u'No to_units (or defaults) for %s', i.dimensionality)
            error = u'No destination units (or defaults) for {}'.format(
                i.dimensionality)

        except DimensionalityError as err:
            log.critical(u'invalid conversion (%s): %s', query, err)
            error = u"Can't convert from {} {} to {} {}".format(
                err.units1, err.dim1, err.units2, err.dim2)

        except KeyError as err:
            log.critical(u'invalid context (%s): %s', i.context, err)
            error = u'Unknown context: {}'.format(i.context)

    if not error and not results:
        error = 'Conversion input not understood'

    if error:  # Show error
        wf.add_item(error,
                    'For example: 2.5cm in  |  178lb kg  |  200m/s mph',
                    valid=False, icon=ICON_WARNING)

    else:  # Show results
        p = CURRENCY_DECIMAL_PLACES if i.is_currency else DECIMAL_PLACES
        f = Formatter(p, DECIMAL_SEPARATOR, THOUSANDS_SEPARATOR,
                      DYNAMIC_DECIMALS)
        wf.setvar('query', query)
        for conv in results:
            value = copytext = f.formatted(conv.to_number, conv.to_unit)
            arg = f.formatted_no_thousands(conv.to_number, conv.to_unit)
            if not COPY_UNIT:
                copytext = f.formatted(conv.to_number)
                arg = f.formatted_no_thousands(conv.to_number)

            it = wf.add_item(value,
                             valid=True,
                             arg=arg,
                             copytext=copytext,
                             largetext=value,
                             icon='icon.png')

            action = 'save'
            name = 'Save'
            if defs.is_default(conv.dimensionality, conv.to_unit):
                action = 'delete'
                name = 'Remove'

            mod = it.add_modifier(
                'cmd',
                u'{} {} as default unit for {}'.format(
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

    wf.magic_arguments['appkey'] = open_currency_instructions

    if not len(wf.args):
        return

    query = wf.args[0]  # .lower()
    log.debug('query : %s', query)

    handle_update(wf)
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
