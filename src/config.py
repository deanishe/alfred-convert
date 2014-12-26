#!/usr/bin/env python
# encoding: utf-8
#
# Copyright © 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-02-25
#

"""
Variables required by more than one script
"""

from __future__ import print_function, unicode_literals

CURRENCY_CACHE_AGE = 3600 * 12  # 12 hours
CURRENCY_CACHE_NAME = 'exchange_rates'


ICON_UPDATE = 'icons/update-available.png'
ICON_CURRENCY = 'icons/money.png'

REFERENCE_CURRENCY = 'EUR'

UPDATE_SETTINGS = {'github_slug': 'deanishe/alfred-convert'}

DEFAULT_SETTINGS = {
    'active_currencies': [
        'AUD',
        'BGN',
        'BRL',
        'CAD',
        'CHF',
        'CNY',
        'CZK',
        'DKK',
        'EUR',
        'GBP',
        'HKD',
        'HRK',
        'HUF',
        'IDR',
        'ILS',
        'INR',
        'JPY',
        'KRW',
        'LTL',
        'MXN',
        'MYR',
        'NOK',
        'NZD',
        'PHP',
        'PLN',
        'RON',
        'RUB',
        'SEK',
        'SGD',
        'THB',
        'TRY',
        'USD',
        'ZAR'
    ]
}
