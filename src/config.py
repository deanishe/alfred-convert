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
UPDATE_STATUS_FILE = 'updating_exchange_rates'
