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

from workflow import Workflow, ICON_WARNING, web
try:
    from xml.etree import cElementTree as ET
except ImportError:
    from xml.etree import ElementTree as ET

log = None

# ECB XML feed settings
XML_URL = 'http://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'
NS_ECB = '{http://www.ecb.int/vocabulary/2002-08-01/eurofxref}'

CURRENCIES = {
    'AUD': 'Australian dollar',
    'BGN': 'Bulgarian lev',
    'BRL': 'Brasilian real',
    'CAD': 'Canadian dollar',
    'CHF': 'Swiss franc',
    'CNY': 'Chinese yuan renminbi',
    'CZK': 'Czech koruna',
    'DKK': 'Danish krone',
    'GBP': 'Pound sterling',
    'HKD': 'Hong Kong dollar',
    'HRK': 'Croatian kuna',
    'HUF': 'Hungarian forint',
    'IDR': 'Indonesian rupiah',
    'ILS': 'Israeli shekel',
    'INR': 'Indian rupee',
    'JPY': 'Japanese yen',
    'KRW': 'South Korean won',
    'LTL': 'Lithuanian litas',
    'MXN': 'Mexican peso',
    'MYR': 'Malaysian ringgit',
    'NOK': 'Norwegian krone',
    'NZD': 'New Zealand dollar',
    'PHP': 'Philippine peso',
    'PLN': 'Polish zloty',
    'RON': 'New Romanian leu 1',
    'RUB': 'Russian rouble',
    'SEK': 'Swedish krona',
    'SGD': 'Singapore dollar',
    'THB': 'Thai baht',
    'TRY': 'Turkish lira',
    'USD': 'US dollar',
    'ZAR': 'South African rand'
}


def fetch_currency_rates():
    """Retrieve today's currency rates from the ECB's homepage

    :returns: `dict` {abbr : ``float``} of currency value in EUR

    """

    exchange_rates = {}

    r = web.get(XML_URL)
    r.raise_for_status()
    root = ET.fromstring(r.content)

    for elem in root.findall('{0}Cube/{0}Cube/{0}Cube'.format(NS_ECB)):
        currency = elem.attrib.get('currency')
        rate = float(elem.attrib.get('rate'))
        print('1 EUR = {0} {1}'.format(rate, currency))
        exchange_rates[currency] = rate

    return exchange_rates


def filter_currencies(query):
    """Return list of currency tuples `(name, abbr)` for supported
    currencies matching `query`

    """

    if not query:
        return [(v, k) for k, v in CURRENCIES.items()]

    currencies = []
    query = query.lower()
    # Currencies that start with query
    for k, v in CURRENCIES.items():
        if k.lower().startswith(query) or v.lower().startswith(query):
            currencies.append((v, k))
    # Currencies that contain query
    for k, v in CURRENCIES.items():
        if query in k.lower() or query in v.lower():
            if (v, k) not in currencies:
                currencies.append((v, k))

    return currencies


def main(wf):
    global log
    log = wf.logger
    query = ''
    if len(wf.args):
        query = wf.args[0]
    currencies = filter_currencies(query)
    if not currencies:
        wf.add_item('No matching currencies found',
                    valid=False, icon=ICON_WARNING)
    else:
        for name, abbr in currencies:
            wf.add_item(abbr, name, valid=False, icon='money.png')

    wf.send_feedback()
    return 0


if __name__ == '__main__':
    wf = Workflow()
    wf.run(main)
