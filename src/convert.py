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

from __future__ import print_function, unicode_literals

import os
import shutil
import sys

from pint import UnitRegistry, UndefinedUnitError, DimensionalityError

from workflow import Workflow3, ICON_WARNING, ICON_INFO
from workflow.background import run_in_background, is_running
from config import (CURRENCIES, CRYPTO_CURRENCIES,
                    CURRENCY_CACHE_AGE, CURRENCY_CACHE_NAME,
                    ICON_UPDATE,
                    UPDATE_SETTINGS, DEFAULT_SETTINGS,
                    BUILTIN_UNIT_DEFINITIONS,
                    CUSTOM_DEFINITIONS_FILENAME,
                    HELP_URL)

log = None

# Pint objects
ureg = UnitRegistry()
ureg.default_format = 'P'
# Q = ureg.Quantity


def register_units():
    """Add built-in and user units to unit registry."""
    # Add custom units from workflow and user data
    ureg.load_definitions(BUILTIN_UNIT_DEFINITIONS)
    user_definitions = wf.datafile(CUSTOM_DEFINITIONS_FILENAME)

    # User's custom units
    if os.path.exists(user_definitions):
        ureg.load_definitions(user_definitions)
    else:  # Copy template to data dir
        shutil.copy(
            wf.workflowfile('{}.sample'.format(CUSTOM_DEFINITIONS_FILENAME)),
            user_definitions)


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


def convert(query, decimal_places=2, auto_convert=None):
    """Parse query, calculate and return conversion result.

    Args:
        query (unicode): Alfred's query.
        decimal_places (int, optional): Number of decimal places in result.

    Raises:
        ValueError: Raised if the query is incomplete or invalid.

    """
    # Parse number from start of query
    qty = []
    for c in query:
        if c in '1234567890.':
            qty.append(c)
        else:
            break
    if not len(qty):
        raise ValueError('Start your query with a number')

    tail = query[len(qty):]
    qty = float(''.join(qty))
    if not len(tail):
        raise ValueError('No units specified')

    log.debug('quantity : %s tail : %s', qty, tail)

    # Try to parse rest of query into a pair of units
    atoms = tail.split()
    from_unit = to_unit = None
    # Try splitting tail at every space until we arrive at a pair
    # of units that `pint` understands. If we only have a single unit,
    # then check to see if perhaps we have a default conversion set
    if len(atoms) == 1:
        if atoms[0] not in auto_convert:
            raise ValueError('No destination unit specified')
        else:
            atoms += auto_convert[atoms[0]]

    q1 = q2 = ''
    for i in range(len(atoms)):
        from_unit = to_unit = None  # reset so no old values spill over
        q1 = ' '.join(atoms[:i + 1]).strip()
        q2 = ' '.join(atoms[i + 1:]).strip()
        log.debug('atoms : %r  i : %d  q1 : %s  q2 : %s', atoms, i, q1, q2)
        if not len(q1) or not len(q2):  # an empty unit
            continue
        try:
            from_unit = ureg.Quantity(qty, q1)
        except UndefinedUnitError:
            continue
        else:
            log.debug('from unit : %s', q1)
            try:
                to_unit = ureg.Quantity(1, q2)
            except UndefinedUnitError:  # Didn't make sense; try again
                raise ValueError('Unknown unit : %s' % q2)

        log.debug("from '%s' to '%s'", from_unit.units, to_unit.units)
        break  # Got something!

    # Throw error if we arrive here with no units
    if from_unit is None:
        raise ValueError('Unknown unit : %s' % q1)
    if to_unit is None:
        raise ValueError('Unknown unit : %s' % q2)
    conv = from_unit.to(to_unit)
    log.debug('%f %s' % (conv.magnitude, conv.units))

    fmt = '%%0.%df %%s' % decimal_places
    result = fmt % (conv.magnitude, conv.units)

    return result


def main(wf):
    """Run workflow Script Filter.

    Args:
        wf (workflow.Workflow): Current Workflow object.

    Returns:
        int: Exit status.
    """
    if not len(wf.args):
        return 1
    query = wf.args[0]  # .lower()
    log.debug('query : %s', query)

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

    if is_running('update'):
        wf.rerun = 0.5
        if exchange_rates is None:  # No data cached yet
            wf.add_item(u'Fetching exchange rates…',
                        'Currency conversions will be momentarily possible',
                        icon=ICON_INFO)
        else:
            wf.add_item(u'Updating exchange rates…',
                        icon=ICON_INFO)

    error = None
    conversion = None

    try:
        conversion = convert(
            query,
            decimal_places=wf.settings.get('decimal_places', 2),
            auto_convert=wf.settings.get('auto_convert', {})
        )
    except UndefinedUnitError as err:
        log.critical('unknown unit : %s', err.unit_names)
        error = 'Unknown unit : {}'.format(err.unit_names)

    except DimensionalityError as err:
        log.critical('invalid conversion : %s', err)
        error = "Can't convert from {} {} to {} {}".format(
            err.units1, err.dim1, err.units2, err.dim2)

    except ValueError as err:
        log.critical('invalid query : %s', err)
        error = err.message

    except Exception as err:
        log.exception('%s : %s', err.__class__, err)
        error = err.message

    if not error and not conversion:
        error = 'Conversion input not understood'

    if error:  # Show error
        wf.add_item(error,
                    'For example: 2.5cm in  |  178lb kg  |  200m/s mph',
                    valid=False, icon=ICON_WARNING)
    else:  # Show result
        wf.add_item(conversion,
                    valid=True,
                    arg=conversion,
                    copytext=conversion,
                    largetext=conversion,
                    icon='icon.png')

    wf.send_feedback()
    log.debug('finished')
    return 0


if __name__ == '__main__':
    wf = Workflow3(update_settings=UPDATE_SETTINGS,
                   default_settings=DEFAULT_SETTINGS,
                   help_url=HELP_URL)
    log = wf.logger
    sys.exit(wf.run(main))
