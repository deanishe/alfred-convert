#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-02-24
#

"""
"""

from __future__ import print_function, unicode_literals

import sys

from pint import UnitRegistry, UndefinedUnitError

from workflow import Workflow, ICON_WARNING, ICON_INFO
from workflow.background import run_in_background, is_running
from config import (CURRENCY_CACHE_AGE, CURRENCY_CACHE_NAME, ICON_UPDATE,
                    UPDATE_SETTINGS, DEFAULT_SETTINGS)

log = None

# Pint objects
ureg = UnitRegistry()
Q = ureg.Quantity


def convert(query):
    """Parse query, calculate and return conversion result

    Raises a `ValueError` if the query is not understood or is invalid (e.g.
    trying to convert between incompatible units).

    :param query: the query entered into Alfred
    :type query: `unicode`
    :returns: the result of the conversion
    :rtype: `unicode`

    """

    global log, ureg, Q
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
    # of units that `pint` understands
    if len(atoms) == 1:
        raise ValueError('No destination unit specified')
    q1 = q2 = ''
    for i in range(len(atoms)):
        from_unit = to_unit = None  # reset so no old values spill over
        q1 = ' '.join(atoms[:i]).strip()
        q2 = ' '.join(atoms[i:]).strip()
        log.debug('atoms : %r  i : %d  q1 : %s  q2 : %s', atoms, i, q1, q2)
        if not len(q1) or not len(q2):  # an empty unit
            continue
        try:
            from_unit = Q(qty, q1)
            to_unit = Q(1, q2)
        except UndefinedUnitError:  # Didn't make sense; try again
            continue
        log.debug("from '%s' to '%s'", from_unit.units, to_unit.units)
        break  # Got something!
    # Throw error if we arrive here with no units
    if from_unit is None:
        raise ValueError('Unknown unit : %s' % q1)
    if to_unit is None:
        raise ValueError('Unknown unit : %s' % q2)
    conv = from_unit.to(to_unit)
    # units = unicode(conv.units)
    # if units.upper() in CURRENCIES:
    #     units = units.upper()
    return '%0.2f %s' % (conv.magnitude, conv.units)


def main(wf):
    global ureg, Q
    # thread = None
    if not len(wf.args):
        return 1
    query = wf.args[0]  # .lower()
    log.debug('query : %s', query)

    # Notify of available update
    if wf.update_available:
        wf.add_item('A newer version is available',
                    'Use query `workflow:update` to install the new version',
                    icon=ICON_UPDATE)

    # Load cached data
    exchange_rates = wf.cached_data(CURRENCY_CACHE_NAME, max_age=0)

    if exchange_rates:  # Add exchange rates to conversion database
        ureg.define('euros = [currency] = eur = EUR')
        for abbr, rate in exchange_rates.items():
            ureg.define('{0} = eur / {1} = {2}'.format(abbr, rate,
                                                       abbr.lower()))

    if not wf.cached_data_fresh(CURRENCY_CACHE_NAME, CURRENCY_CACHE_AGE):
        # Update currency rates
        cmd = ['/usr/bin/python', wf.workflowfile('update_exchange_rates.py')]
        run_in_background('update', cmd)

    if is_running('update'):
        if exchange_rates is None:  # No data cached yet
            wf.add_item('Fetching exchange rates…',
                        'Currency conversions will be momentarily possible',
                        icon=ICON_INFO)
        else:
            wf.add_item('Updating exchange rates…',
                        icon=ICON_INFO)

    error = None
    conversion = None

    try:
        conversion = convert(query)
    except UndefinedUnitError as err:
        log.critical('Unknown unit : %s', err.unit_names)
        error = 'Unknown unit : {}'.format(err.unit_names)

    except ValueError as err:
        log.critical('Invalid query : %s', err)
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
    wf = Workflow(update_settings=UPDATE_SETTINGS,
                  default_settings=DEFAULT_SETTINGS)
    log = wf.logger
    sys.exit(wf.run(main))
