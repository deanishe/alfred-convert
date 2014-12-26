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
from itertools import izip_longest
import re

from workflow import Workflow, web

from config import (CURRENCY_CACHE_NAME,
                    CURRENCY_CACHE_AGE,
                    REFERENCE_CURRENCY,
                    CURRENCIES,
                    YAHOO_BASE_URL,
                    SYMBOLS_PER_REQUEST)


log = None

parse_yahoo_response = re.compile(r'{}(.+)=X'.format(REFERENCE_CURRENCY)).match


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

        if not m:  # Couldn't get symbol
            log.error('Invalid currency : {}'.format(name))
            ycount += 1
            continue
        symbol = m.group(1)
        rate = float(rate)

        if rate == 0:  # Yahoo! returns 0.0 as rate for unsupported currencies
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

    log.debug('Fetching exchange rates from Yahoo! ...')

    exchange_rates = wf.cached_data(CURRENCY_CACHE_NAME,
                                    fetch_currency_rates,
                                    CURRENCY_CACHE_AGE)

    log.debug('Exchange rates updated.')

    for currency, rate in exchange_rates.items():
        wf.logger.debug('1 EUR = {0} {1}'.format(rate, currency))


if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    wf.run(main)
