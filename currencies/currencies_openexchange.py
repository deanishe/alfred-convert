#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-11-02
#

"""
Take list of all/wanted currencies and filter it by whether
openexchangerates.org offers exchange rates.
"""

from __future__ import print_function, absolute_import

import csv
import os
import requests
import sys

reference_currency = 'USD'
api_key = None

api_url = 'https://openexchangerates.org/api/latest.json?app_id={api_key}'

# Source files
currency_source_files = [
    os.path.join(os.path.dirname(__file__), n) for n in [
        'currencies_iso_4217.tsv',
        'currencies_custom.tsv',
    ]
]

# Destination file
openx_currencies_file = os.path.join(os.path.dirname(__file__),
                                     'currencies_openexchange.tsv')


def log(s, *args):
    """Simple STDERR logger."""
    if args:
        s = s % args
    print(s, file=sys.stderr)


def load_currencies(*filepaths):
    """Read currencies from TSV files.

    Args:
        *filepaths: TSV files containing currencies, e.g.
        `XXX    Currency Name`

    Returns:
        dict: `{symbol: name}` mapping of currencies.
    """
    currencies = {}
    for filepath in filepaths:
        with open(filepath, 'rb') as fp:
            reader = csv.reader(fp, delimiter=b'\t')
            for row in reader:
                symbol, name = [unicode(s, 'utf-8') for s in row]
                currencies[symbol] = name

    return currencies


def get_exchange_rates(symbols):
    """Fetch exchange rates from openexchangerates.org.

    Args:
        symbols: Set of currency symbols to return.

    Returns:
        dict: `{symbol: rate}` mapping, e.g. `{'USD': 0.9}`
    """
    rates = {}
    wanted = set(symbols)
    url = api_url.format(api_key=api_key)
    r = requests.get(url)
    r.raise_for_status()

    data = r.json()
    for sym, rate in data['rates'].items():
        if sym not in wanted:
            log('unwanted currency: %s', sym)
            continue

        rates[sym] = rate

    return rates


def main():
    """Generate list of currencies supported by Yahoo! Finance."""
    unknown_currencies = []
    all_currencies = load_currencies(*currency_source_files)

    to_check = all_currencies
    log('%d currencies to check ...', len(to_check))

    rates = get_exchange_rates(to_check)
    for symbol in sorted(rates):
        rate = rates[symbol]
        if rate == 0:
            unknown_currencies.append(symbol)
        else:
            print('{0}\t{1}'.format(symbol, rate))

    if len(unknown_currencies):
        log('\n\nUnsupported currencies:')
        log('-----------------------')
        for symbol in unknown_currencies:
            log('%s\t%s', symbol, all_currencies[symbol])

    supported_currencies = {k: v for k, v in all_currencies.items()
                            if k not in unknown_currencies}

    with open(openx_currencies_file, 'wb') as fp:
        w = csv.writer(fp, delimiter=b'\t')
        for sym in sorted(supported_currencies):
            name = supported_currencies[sym]
            r = [sym.encode('utf-8'), name.encode('utf-8')]
            w.writerow(r)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: currencies_openexchange.py <APP_KEY>')
        sys.exit(1)
    api_key = sys.argv[1]
    main()
