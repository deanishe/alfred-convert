#!/usr/bin/env python
# encoding: utf-8
#
# Copyright  (c) 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-02-24
#

"""Script to update exchange rates in the background."""

from __future__ import print_function

from itertools import izip_longest
from multiprocessing.dummy import Pool
import os
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
    OPENX_API_URL,
    OPENX_APP_KEY,
    SYMBOLS_PER_REQUEST,
    USER_AGENT,
    XRA_API_URL,
)


log = None


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


def load_cryptocurrency_rates(symbols):
    """Return dict of exchange rates from CryptoCompare.com.

    Args:
        symbols (sequence): Abbreviations of currencies to fetch
            exchange rates for, e.g. 'BTC' or 'DOGE'.

    Returns:
        dict: `{symbol: rate}` mapping of exchange rates.

    """
    url = CRYPTO_COMPARE_BASE_URL.format(REFERENCE_CURRENCY, ','.join(symbols))

    log.debug('fetching %s ...', url)
    r = web.get(url, headers={'User-Agent': USER_AGENT})
    r.raise_for_status()

    data = r.json()
    for sym, rate in data.items():
        log.debug('[CryptoCompare.com] 1 %s = %s %s',
                  REFERENCE_CURRENCY, rate, sym)

    return data


def load_xra_rates(symbols):
    """Return dict of exchange rates from exchangerate-api.com.

    Returns:
        dict: `{symbol: rate}` mapping of exchange rates.

    """
    rates = {}
    wanted = set(symbols)
    url = XRA_API_URL.format(REFERENCE_CURRENCY)
    r = web.get(url, headers={'User-Agent': USER_AGENT})
    r.raise_for_status()
    log.debug('[%s] %s', r.status_code, url)
    data = r.json()

    for sym, rate in data['rates'].items():
        if sym not in wanted:
            continue
        log.debug('[ExchangeRate-API.com] 1 %s = %s %s',
                  REFERENCE_CURRENCY, rate, sym)
        rates[sym] = rate

    return rates


def load_openx_rates(symbols):
    """Return dict of exchange rates from openexchangerates.org.

    Args:
        symbols (sequence): Abbreviations of currencies to fetch
            exchange rates for, e.g. 'USD' or 'GBP'.

    Returns:
        dict: `{symbol: rate}` mapping of exchange rates.

    """
    rates = {}
    wanted = set(symbols)
    if not OPENX_APP_KEY:
        log.warning(
            'not fetching fiat currency exchange rates: '
            'APP_KEY for openexchangerates.org not set. '
            'Please sign up for a free account here: '
            'https://openexchangerates.org/signup/free'
        )
        return rates

    url = OPENX_API_URL.format(OPENX_APP_KEY)
    r = web.get(url, headers={'User-Agent': USER_AGENT})
    r.raise_for_status()
    log.debug('[%s] %s', r.status_code, OPENX_API_URL.format('XXX'))
    data = r.json()

    for sym, rate in data['rates'].items():
        if sym not in wanted:
            continue
        log.debug('[OpenExchangeRates.org] 1 %s = %s %s',
                  REFERENCE_CURRENCY, rate, sym)
        rates[sym] = rate

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
            if not line or line.startswith('#'):
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

    syms = [s for s in CURRENCIES.keys() if s in active]
    if not OPENX_APP_KEY:
        log.warning(
            'fetching limited set of fiat currency exchange rates: '
            'APP_KEY for openexchangerates.org not set. '
            'Please sign up for a free account here: '
            'https://openexchangerates.org/signup/free'
        )
        jobs = [(load_xra_rates, (syms,))]
    else:
        jobs = [(load_openx_rates, (syms,))]

    syms = []
    for s in CRYPTO_CURRENCIES.keys():
        if s in CURRENCIES:
            log.warning('ignoring crytopcurrency "%s", as it conflicts with '
                        'a fiat currency', s)
            continue
        if s in active:
            syms.append(s)
    # syms = [s for s in CRYPTO_CURRENCIES.keys() if s in active]
    for symbols in grouper(SYMBOLS_PER_REQUEST, syms):
        jobs.append((load_cryptocurrency_rates, (symbols,)))

    # fetch data in a thread pool
    pool = Pool(2)
    for job in jobs:
        futures.append(pool.apply_async(*job))

    pool.close()
    pool.join()

    for f in futures:
        rates.update(f.get())

    return rates


def main(wf):
    """Update exchange rates.

    Args:
        wf (workflow.Workflow): Workflow object.

    """
    start_time = time.time()
    bootstrap(wf)

    site = 'OpenExchangeRates.org' if OPENX_APP_KEY else 'ExchangeRate-API.com'

    log.info('fetching exchange rates from %s and CryptoCompare.com ...',
             site)

    rates = wf.cached_data(CURRENCY_CACHE_NAME,
                           fetch_exchange_rates,
                           CURRENCY_CACHE_AGE)

    elapsed = time.time() - start_time
    log.info('%d exchange rates updated in %0.2f seconds.',
             len(rates), elapsed)

    for currency, rate in sorted(rates.items()):
        log.debug('1 %s = %s %s', REFERENCE_CURRENCY, rate, currency)


if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    wf.run(main)
