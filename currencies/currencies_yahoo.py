#!/usr/bin/env python
# encoding: utf-8
#
# Copyright  (c) 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-12-26
#

"""
Take list of all/wanted currencies and filter it by whether Yahoo!
Finance offers exchange rates.
"""

from __future__ import print_function, unicode_literals, absolute_import

import csv
from itertools import izip_longest
import json
import os
import re
import requests
import sys

reference_currency = 'EUR'

# Source files
currency_source_files = [
    os.path.join(os.path.dirname(__file__), n) for n in [
        'currencies_iso_4217.tsv',
        'currencies_custom.tsv',
    ]
]

# Destination file
yahoo_currencies_file = os.path.join(os.path.dirname(__file__),
                                     'currencies_yahoo.tsv')

yahoo_base_url = 'https://download.finance.yahoo.com/d/quotes.csv?f=sl1&s={}'

# Max = 50
symbols_per_request = 50

parse_yahoo_response = re.compile(r'{}(.+)=X'.format(reference_currency)).match


def grouper(n, iterable, fillvalue=None):
    """Split `iterable` into sequences of length `n`.

    Args:
        n (int): Size of each group.
        iterable (iterable): Iterable to split into groups.
        fillvalue (any, optional): Value to pad shorter iterators with.

    Returns:
        iterator: Yields tuples of size `n`.
    """
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)


def load_yahoo_rates(symbols):
    """Fetch exchange rates for `symbols` from Yahoo! Finance.

    Args:
        symbols (sequence): Symbols (e.g. USD, GBP) of currencies.

    Returns:
        dict: `{symbol: rate}` mapping rates, e.g. {'USD': 0.8}
    """
    rates = {}
    count = len(symbols)

    # Build URL
    parts = []
    for symbol in symbols:
        if symbol == reference_currency:
            count -= 1
            continue
        parts.append('{}{}=X'.format(reference_currency, symbol))
    query = ','.join(parts)
    url = yahoo_base_url.format(query)

    # Fetch data
    print('Fetching {} ...'.format(url), file=sys.stderr)
    r = requests.get(url)
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
            print('Invalid currency : {}'.format(name), file=sys.stderr)
            continue
        symbol = m.group(1)
        try:
            rate = float(rate)
        except ValueError:  # Result was "N/A"
            rate = 0

        rates[symbol] = rate
        ycount += 1
        # print(row)

    assert ycount == count, 'Yahoo! returned {} results, not {}'.format(
        ycount, count)

    return rates


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
    """Fetch exchange rates from Yahoo! Finance.

    Args:
        symbols (sequence): Currency symbols, e.g. USD or EUR.

    Returns:
        dict: `{symbol: rate}` mapping, e.g. `{'USD': 0.9}`
    """
    rates = {}
    for symbols in grouper(symbols_per_request, symbols):
        symbols = [s for s in symbols if s]
        d = load_yahoo_rates(symbols)
        rates.update(d)
    return rates


def main():
    """Generate list of currencies supported by Yahoo! Finance."""
    unknown_currencies = []
    all_currencies = load_currencies(*currency_source_files)

    to_check = all_currencies
    print('{} currencies to check ...'.format(len(to_check)), file=sys.stderr)

    rates = get_exchange_rates(to_check)
    for symbol in sorted(rates):
        rate = rates[symbol]
        if rate == 0:
            unknown_currencies.append(symbol)
        else:
            print('{}\t{}'.format(symbol, rate))

    print('\n\nUnsupported currencies:')
    print('-----------------------')
    for symbol in unknown_currencies:
        print('{}\t{}'.format(symbol, all_currencies[symbol]))

    supported_currencies = {k: v for k, v in all_currencies.items()
                            if k not in unknown_currencies}

    with open(yahoo_currencies_file, 'wb') as fp:
        w = csv.writer(fp, delimiter=b'\t')
        for sym in sorted(supported_currencies):
            name = supported_currencies[sym]
            r = [sym.encode('utf-8'), name.encode('utf-8')]
            w.writerow(r)


if __name__ == '__main__':
    main()
