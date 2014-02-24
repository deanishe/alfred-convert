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
import threading

from pint import UnitRegistry, UndefinedUnitError

from workflow import Workflow, ICON_WARNING, ICON_INFO
from currency import fetch_currency_rates

log = None

CURRENCY_CACHE_AGE = 3600 * 12  # 12 hours
CURRENCY_CACHE_NAME = 'exchange_rates'
# Pint objects
ureg = UnitRegistry()
Q = ureg.Quantity


def convert(query):
    """Parse query into `quantity`, `from_unit`, `to_unit`"""
    global log, ureg, Q
    # Parse number from start of query
    qty = []
    for c in query:
        if c in '1234567890.':
            qty.append(c)
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


def update_exchange_rates(wf, ureg):
    global log
    exchange_rates = wf.cached_data(CURRENCY_CACHE_NAME, fetch_currency_rates,
                                    CURRENCY_CACHE_AGE)
    # EUR is reference
    ureg.define('euros = [currency] = eur = EUR')
    for abbr, rate in exchange_rates.items():
        ureg.define('{0} = eur * {1} = {2}'.format(abbr, rate,
                                                   abbr.lower()))
        log.debug('1 EUR = {0} {1}'.format(rate, abbr))


def main(wf):
    global log, ureg, Q
    log = wf.logger
    if not len(wf.args):
        return 1
    query = wf.args[0].lower()
    log.debug('query : %s', query)

    if wf.cached_data_age(CURRENCY_CACHE_NAME) > CURRENCY_CACHE_AGE:
        # Get exchange rates and register them
        thread = threading.Thread(target=update_exchange_rates, args=(wf, ureg))
        thread.daemon = False
        thread.start()
        wf.add_item('Updating exchange rates…', valid=False, icon=ICON_INFO)

    else:  # Run synchronously
        thread = None
        update_exchange_rates(wf, ureg)

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
        wf.add_item(conversion, valid=False, icon='icon.png')

    wf.send_feedback()
    if thread:
        thread.join()
    return 0


if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
