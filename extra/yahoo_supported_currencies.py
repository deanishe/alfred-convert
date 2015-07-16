#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-12-26
#

"""
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

all_currencies_file = os.path.join(os.path.dirname(__file__),
                                   'ISO 4217 Currencies.tsv')

ecb_currencies_file = os.path.join(os.path.dirname(__file__),
                                   'currencies_ecb.json')

yahoo_currencies_file = os.path.join(os.path.dirname(__file__),
                                     'currencies_yahoo.json')

yahoo_base_url = 'https://download.finance.yahoo.com/d/quotes.csv?f=sl1&s={}'

symbols_per_request = 50

parse_yahoo_response = re.compile(r'{}(.+)=X'.format(reference_currency)).match


def grouper(n, iterable, fillvalue=None):
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)


def load_yahoo_rates(symbols):
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
        rate = float(rate)
        rates[symbol] = rate
        ycount += 1
        # print(row)

    assert ycount == count, 'Yahoo! returned {} results, not {}'.format(
        ycount, count)

    return rates


def load_all_currencies():
    currencies = {}
    with open(all_currencies_file, 'rb') as fp:
        reader = csv.reader(fp, delimiter=b'\t')
        for row in reader:
            symbol, name = [unicode(s, 'utf-8') for s in row]
            currencies[symbol] = name

    return currencies


def get_exchange_rates(symbols):
    rates = {}
    for symbols in grouper(symbols_per_request, symbols):
        symbols = [s for s in symbols if s]
        d = load_yahoo_rates(symbols)
        rates.update(d)
    return rates


def main():
    unknown_currencies = []
    all_currencies = load_all_currencies()
    with open(ecb_currencies_file, 'rb') as fp:
        ecb_currencies = json.load(fp)

    to_check = [k for k in all_currencies if k not in ecb_currencies]
    to_check = all_currencies
    print('{} currencies to check ...'.format(len(to_check)), file=sys.stderr)
    rates = get_exchange_rates(to_check)
    for symbol in sorted(rates):
        rate = rates[symbol]
        if rate == 0:
            unknown_currencies.append(symbol)
        else:
            print('{}\t{}'.format(symbol, rate))

    print('\n\nUnsupported currencies')
    for symbol in unknown_currencies:
        print('{}\t{}'.format(symbol, all_currencies[symbol]))

    supported_currencies = {k: v for k, v in all_currencies.items()
                            if k not in unknown_currencies}

    with open(yahoo_currencies_file, 'wb') as fp:
        json.dump(supported_currencies, fp, indent=2, sort_keys=True)


if __name__ == '__main__':
    main()
