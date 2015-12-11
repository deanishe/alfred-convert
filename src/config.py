#!/usr/bin/env python
# encoding: utf-8
#
# Copyright  (c) 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-02-25
#

"""Variables required by more than one script."""

from __future__ import print_function, unicode_literals

import csv
import os

# ----------------------------------------------------------------------
# Keywords assigned to Alfred Keywords/Script Filters
# ----------------------------------------------------------------------
KEYWORD_CONVERT = 'conv'
KEYWORD_SETTINGS = 'convinfo'

# ----------------------------------------------------------------------
# Result display
# ----------------------------------------------------------------------
DECIMAL_PLACES_DEFAULT = 2

# ----------------------------------------------------------------------
# Currency settings
# ----------------------------------------------------------------------
CURRENCY_CACHE_AGE = 3600 * 12  # 12 hours
CURRENCY_CACHE_NAME = 'exchange_rates'
REFERENCE_CURRENCY = 'EUR'
YAHOO_BASE_URL = 'https://download.finance.yahoo.com/d/quotes.csv?f=sl1&s={0}'
SYMBOLS_PER_REQUEST = 50

# ----------------------------------------------------------------------
# Unit definition files
# ----------------------------------------------------------------------
CURRENCIES = {}
CUSTOM_DEFINITIONS_FILENAME = 'unit_definitions.txt'
BUILTIN_UNIT_DEFINITIONS = os.path.join(os.path.dirname(__file__),
                                        CUSTOM_DEFINITIONS_FILENAME)

with open(os.path.join(os.path.dirname(__file__),
                       'currencies.tsv'), 'rb') as fp:
    reader = csv.reader(fp, delimiter=b'\t')
    for sym, name in reader:
        sym = unicode(sym, 'utf-8')
        name = unicode(name, 'utf-8')
        CURRENCIES[sym] = name

# ----------------------------------------------------------------------
# Help/support URLs
# ----------------------------------------------------------------------
HELP_URL = 'https://github.com/deanishe/alfred-convert/issues'
README_URL = 'https://github.com/deanishe/alfred-convert#alfred-convert'

# ----------------------------------------------------------------------
# Icons
# ----------------------------------------------------------------------
ICON_UPDATE = 'icons/update-available.png'
ICON_CURRENCY = 'icons/money.png'

# ----------------------------------------------------------------------
# Update and default user settings
# ----------------------------------------------------------------------
UPDATE_SETTINGS = {'github_slug': 'deanishe/alfred-convert'}
DEFAULT_SETTINGS = {
    'decimal_places': DECIMAL_PLACES_DEFAULT,
}
