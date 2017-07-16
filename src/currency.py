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

from __future__ import print_function

import csv
from itertools import chain, izip_longest
from multiprocessing.dummy import Pool
import os
import re
import shutil
import time

from workflow import Workflow, web

from config import (
    bootstrap,
    ACTIVE_CURRENCIES_FILENAME,
    CURRENCY_CACHE_AGE,
    CURRENCY_CACHE_NAME,
    REFERENCE_CURRENCY,
    CURRENCIES,
    CRYPTO_CURRENCIES,
    CRYPTO_COMPARE_BASE_URL,
    YAHOO_BASE_URL,
    SYMBOLS_PER_REQUEST,
)


log = None

parse_yahoo_response = re.compile(REFERENCE_CURRENCY + '(.+)=X').match


def grouper(n, iterable):
    """Return iterable that splits `iterable` into groups of size `n`.

    Args:
        n (int): Size of each group.
        iterable (iterable): The iterable to split into groups.

    Returns:
        list: Tuples of length `n` containing items
            from `iterable`.

    """
    sentinel = object()
    args = [iter(iterable)] * n
    groups = []
    for l in izip_longest(*args, fillvalue=sentinel):
        groups.append([v for v in l if v is not sentinel])
    return groups


def interleave(*iterables):
    """Interleave elements of ``iterables``.

    Args:
        *iterables: Iterables to interleave

    Returns:
        list: Elements of ``iterables`` interleaved

    """
    sentinel = object()
    it = izip_longest(*iterables, fillvalue=sentinel)
    c = chain.from_iterable(it)
    return list(filter(lambda v: v is not sentinel, c))


def load_cryptocurrency_rates(symbols):
    """Return dict of exchange rates from CryptoCompare.com.

    Args:
        symbols (sequence): Abbreviations of currencies to fetch
            exchange rates for, e.g. 'BTC' or 'DOGE'.

    Returns:
        dict: `{symbol: rate}` mapping of exchange rates.

    """
    url = CRYPTO_COMPARE_BASE_URL.format(REFERENCE_CURRENCY, ','.join(symbols))

    r = web.get(url)
    r.raise_for_status()

    data = r.json()
    log.debug('fetching %s ...', url)
    return data


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
        parts.append('{}{}=X'.format(REFERENCE_CURRENCY, symbol))

    query = ','.join(parts)
    url = YAHOO_BASE_URL.format(query)

    # Fetch data
    # log.debug('Fetching %s ...', url)
    log.debug('fetching %s ...', url)
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
            log.error(u'invalid currency : %s', name)
            ycount += 1
            continue
        symbol = m.group(1)

        # Yahoo! returns "N/A" for unsupported currencies.
        # That's handled in the script that generates the
        # currency list, however: an invalid currency shouldn't end up here
        # unless Yahoo! has changed the supported currencies.

        try:
            rate = float(rate)
        except ValueError:
            log.error(u'no exchange rate: %s', name)
            continue

        if rate == 0:
            log.error(u'no exchange rate: %s', name)
            ycount += 1
            continue

        rates[symbol] = rate
        ycount += 1

    assert ycount == count, 'Yahoo! returned {} results, not {}'.format(
        ycount, count)

    return rates


def load_active_currencies():
    """Load active currencies from user settings (or defaults).

    Returns:
        set: Symbols for active currencies.

    """
    symbols = set()

    user_currencies = wf.datafile(ACTIVE_CURRENCIES_FILENAME)
    if not os.path.exists(user_currencies):
        return symbols

    with open(user_currencies) as fp:
        for line in fp:
            line = line.strip()
            if line.startswith('#'):
                continue

            symbols.add(line.upper())

    return symbols


def fetch_exchange_rates():
    """Retrieve all currency exchange rates.

    Batch currencies into requests of `SYMBOLS_PER_REQUEST` currencies each.

    Returns:
        list: List of `{abbr : n.nn}` dicts of exchange rates
            (relative to EUR).

    """
    rates = {}
    futures = []
    active = load_active_currencies()

    # batch symbols into groups and interleave requests to the
    # different services
    yjobs = []
    syms = [s for s in CURRENCIES.keys() if s in active]
    for symbols in grouper(SYMBOLS_PER_REQUEST, syms):
        yjobs.append((load_yahoo_rates, (symbols,)))

    cjobs = []
    syms = [sym for sym in CRYPTO_CURRENCIES.keys() if sym in active]
    for symbols in grouper(SYMBOLS_PER_REQUEST, syms):
        cjobs.append((load_cryptocurrency_rates, (symbols,)))

    # fetch data in a thread pool
    pool = Pool(4)
    for job in interleave(yjobs, cjobs):
        futures.append(pool.apply_async(*job))

    pool.close()
    pool.join()

    for f in futures:
        rates.update(f.get())

    return rates


def main(wf):
    """Update exchange rates from Yahoo! Finance.

    Args:
        wf (workflow.Workflow): Workflow object.

    """
    start_time = time.time()
    bootstrap(wf)

    log.info('fetching exchange rates from Yahoo! and CryptoCompare.com ...')

    rates = wf.cached_data(CURRENCY_CACHE_NAME,
                           fetch_exchange_rates,
                           CURRENCY_CACHE_AGE)

    elapsed = time.time() - start_time
    log.info('%d exchange rates updated in %0.2f seconds.',
             len(rates), elapsed)

    for currency, rate in sorted(rates.items()):
        log.debug('1 EUR = %s %s', rate, currency)


if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    wf.run(main)
