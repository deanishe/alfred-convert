#!/usr/bin/env python
# encoding: utf-8
#
# Copyright  (c) 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-02-24
#

"""Script to update exchange rates from Yahoo! in the background."""

from __future__ import print_function, unicode_literals

import csv
from itertools import izip_longest
import re
import time

from workflow import Workflow, web

from config import (CURRENCY_CACHE_NAME,
                    CURRENCY_CACHE_AGE,
                    REFERENCE_CURRENCY,
                    CURRENCIES,
                    YAHOO_BASE_URL,
                    SYMBOLS_PER_REQUEST)


log = None

parse_yahoo_response = re.compile(r'{0}(.+)=X'.format(REFERENCE_CURRENCY)).match


def grouper(n, iterable, fillvalue=None):
    """Return iterable that splits `iterable` into groups of size `n`.

    Args:
        n (int): Size of each group.
        iterable (iterable): The iterable to split into groups.
        fillvalue (object, optional): Value to pad short sequences with.

    Returns:
        iterator: Yields tuples of length `n` containing items
            from `iterable`.
    """

    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)


def load_yahoo_rates(symbols):
    """Return dict of exchange rates from Yahoo! Finance.

    Args:
        symbols (sequence): Abbreviations of currencies to fetch
            exchange rates for, e.g. 'USD' or 'GBP'.

    Returns:
        dict: `{symbol: rate}` mapping of exchange rates.
    """

    rates = {}
    count = len(symbols)

    # Build URL
    parts = []
    for symbol in symbols:
        if symbol == REFERENCE_CURRENCY:
            count -= 1
            continue
        parts.append('{0}{1}=X'.format(REFERENCE_CURRENCY, symbol))

    query = ','.join(parts)
    url = YAHOO_BASE_URL.format(query)

    # Fetch data
    # log.debug('Fetching {0} ...'.format(url))
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
            log.error('Invalid currency : {0}'.format(name))
            ycount += 1
            continue
        symbol = m.group(1)

        # Yahoo! returns 0.0 as rate for unsupported currencies
        # NOTE: This has changed. "N/A" is now returned for
        # unsupported currencies. That's handled in the script
        # that generates the currency list, however: an invalid
        # currency should never end up here.

        try:
            rate = float(rate)
        except ValueError:
            log.error('No exchange rate for : {0}'.format(name))
            continue

        if rate == 0:
            log.error('No exchange rate for : {0}'.format(name))
            ycount += 1
            continue

        rates[symbol] = rate
        ycount += 1

    assert ycount == count, 'Yahoo! returned {0} results, not {1}'.format(
        ycount, count)

    return rates


def fetch_currency_rates():
    """Retrieve all currency exchange rates.

    Batch currencies into requests of `SYMBOLS_PER_REQUEST` currencies each.

    Returns:
        list: List of `{abbr : n.nn}` dicts of exchange rates
            (relative to EUR).
    """

    rates = {}

    for symbols in grouper(SYMBOLS_PER_REQUEST, CURRENCIES.keys()):
        symbols = [s for s in symbols if s]
        d = load_yahoo_rates(symbols)
        rates.update(d)

    return rates


def main(wf):
    """Update exchange rates from Yahoo! Finance.

    Args:
        wf (workflow.Workflow): Workflow object.
    """
    start_time = time.time()
    log.info('Fetching exchange rates from Yahoo! ...')

    exchange_rates = wf.cached_data(CURRENCY_CACHE_NAME,
                                    fetch_currency_rates,
                                    CURRENCY_CACHE_AGE)

    elapsed = time.time() - start_time
    log.info('%d exchange rates updated in %0.2f seconds.',
             len(exchange_rates), elapsed)

    for currency, rate in exchange_rates.items():
        wf.logger.debug('1 EUR = {0} {1}'.format(rate, currency))


if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    wf.run(main)
