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

import json
import os

CURRENCY_CACHE_AGE = 3600 * 12  # 12 hours
CURRENCY_CACHE_NAME = 'exchange_rates'

with open(os.path.join(os.path.dirname(__file__),
                       'currencies.json'), 'rb') as fp:
    CURRENCIES = json.load(fp)


ICON_UPDATE = 'icons/update-available.png'
ICON_CURRENCY = 'icons/money.png'

REFERENCE_CURRENCY = 'EUR'

YAHOO_BASE_URL = 'http://download.finance.yahoo.com/d/quotes.csv?f=sl1&s={}'

SYMBOLS_PER_REQUEST = 50

UPDATE_SETTINGS = {'github_slug': 'deanishe/alfred-convert'}

DEFAULT_SETTINGS = {}
