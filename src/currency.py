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

import csv
from datetime import timedelta
from itertools import izip_longest
import re

from workflow import (Workflow, web,
                      ICON_WARNING, ICON_INFO,
                      MATCH_ALL, MATCH_ALLCHARS)

from config import (CURRENCY_CACHE_NAME,
                    ICON_CURRENCY,
                    REFERENCE_CURRENCY,
                    CURRENCIES,
                    YAHOO_BASE_URL,
                    SYMBOLS_PER_REQUEST)


wf = Workflow()
log = wf.logger

parse_yahoo_response = re.compile(r'{}(.+)=X'.format(REFERENCE_CURRENCY)).match


def human_timedelta(td):
    output = []
    d = {'day': td.days}
    d['hour'], rem = divmod(td.seconds, 3600)
    d['minute'], d['second'] = divmod(rem, 60)
    for unit in ('day', 'hour', 'minute', 'second'):
        i = d[unit]
        if unit == 'second' and len(output):
            # no seconds unless last update was < 1m ago
            break
        if i == 1:
            output.append('1 %s' % unit)
        elif i > 1:
            output.append('%d %ss' % (i, unit))
    output.append('ago')
    return ' '.join(output)


def grouper(n, iterable, fillvalue=None):
    """Return iterable that groups ``iterable`` into groups of length ``n``

    :param n: Size of group
    :type n: ``int``
    :param iterable: Iterable to split into groups
    :param fillvalue: Value to pad groups with if there aren't enough values
        in ``iterable``
    :returns: Iterator

    """

    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)


def load_yahoo_rates(symbols):
    """Return dict of exchange rates from Yahoo!

    :param symbols: List of symbols, e.g. ``['GBP', 'USD', ...]``
    :returns: Dictionary of rates: ``{'GBP': 1.12, 'USD': 3.2}``

    """

    rates = {}
    count = len(symbols)

    # Build URL
    parts = []
    for symbol in symbols:
        if symbol == REFERENCE_CURRENCY:
            count -= 1
            continue
        parts.append('{}{}=X'.format(REFERENCE_CURRENCY, symbol))
    query = ','.join(parts)
    url = YAHOO_BASE_URL.format(query)

    # Fetch data
    # log.debug('Fetching {} ...'.format(url))
    r = web.get(url)
    r.raise_for_status()

    # Parse response
    lines = r.content.split('\n')
    ycount = 0
    for row in csv.reader(lines):
        if not row:
            continue
        name, rate = row
        m = parse_yahoo_response(name)
        if not m:
            log.error('Invalid currency : {}'.format(name))
            ycount += 1
            continue
        symbol = m.group(1)
        rate = float(rate)
        if rate == 0:
            log.error('No exchange rate for : {}'.format(name))
            ycount += 1
            continue
        rates[symbol] = rate
        ycount += 1

    assert ycount == count, 'Yahoo! returned {} results, not {}'.format(
        ycount, count)

    return rates


def fetch_currency_rates():
    """Retrieve today's currency rates from the ECB's homepage

    :returns: `dict` {abbr : ``float``} of currency value in EUR

    """

    rates = {}

    for symbols in grouper(SYMBOLS_PER_REQUEST, CURRENCIES.keys()):
        symbols = [s for s in symbols if s]
        d = load_yahoo_rates(symbols)
        rates.update(d)

    return rates


def main(wf):
    global log
    log = wf.logger
    query = ''
    if len(wf.args):
        query = wf.args[0]

    currencies = CURRENCIES.items()

    if query:
        currencies = wf.filter(query, currencies,
                               key=lambda t: ' '.join(t),
                               match_on=MATCH_ALL ^ MATCH_ALLCHARS,
                               min_score=30)

    # currencies = filter_currencies(query)
    if not currencies:
        wf.add_item('No matching currencies found',
                    valid=False, icon=ICON_WARNING)
    else:
        if not query:  # Show last update time
            td = timedelta(seconds=wf.cached_data_age(CURRENCY_CACHE_NAME))
            # currencies_updated = datetime.now() - timedelta(seconds=age)
            wf.add_item('Exchange rates updated %s' % human_timedelta(td),
                        valid=False, icon=ICON_INFO)
        for name, abbr in currencies:
            # wf.add_item(abbr, name, valid=False, icon='money.png')
            wf.add_item('%s — %s' % (abbr, name),
                        'Use the 3-letter currency code in conversions',
                        valid=False, icon=ICON_CURRENCY)

    wf.send_feedback()
    return 0


if __name__ == '__main__':
    wf.run(main)
