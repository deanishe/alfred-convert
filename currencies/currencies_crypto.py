#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-07-14
#

"""
Filter list of cryptocurrencies by whether an exchange rate is available.
"""

from __future__ import print_function, absolute_import

from collections import namedtuple
import csv
from itertools import izip_longest
import os
import requests
from time import sleep

reference_currency = 'USD'

all_currencies_url = 'https://www.cryptocompare.com/api/data/coinlist/'
base_url = 'https://min-api.cryptocompare.com/data/price?fsym={}&tsyms={}'

crypto_currencies_file = os.path.join(os.path.dirname(__file__),
                                      'currencies_crypto.tsv')


Currency = namedtuple('Currency', 'symbol name')


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


def main():
    """Generate list of cryptocurrencies with exchange rates."""
    r = requests.get(all_currencies_url)
    r.raise_for_status()
    data = r.json()
    all_currencies = []
    valid = []
    invalid = set()
    for k, d in data['Data'].items():
        all_currencies.append(Currency(k, d['CoinName']))

    print('%d total currencies' % len(all_currencies))

    # for c in sorted(all_currencies):
    for currencies in grouper(20, all_currencies):
        url = base_url.format(reference_currency,
                              ','.join([c.symbol for c in currencies]))
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()
        for c in currencies:
            if c.symbol in data:
                valid.append(c)
                print('[%s] OK' % c.symbol)
            else:
                invalid.add(c)
                print('[%s] ERROR' % c.symbol)

        sleep(0.3)

    # valid = [c for c in all_currencies if c.symbol not in invalid]
    with open(crypto_currencies_file, 'wb') as fp:
        w = csv.writer(fp, delimiter='\t')
        for c in sorted(valid, key=lambda t: t.symbol):
            r = [c.symbol.encode('utf-8'), c.name.encode('utf-8')]
            w.writerow(r)


if __name__ == '__main__':
    main()
