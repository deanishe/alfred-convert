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
Runs as daemon process in the background and updates exchange rates.
"""

from __future__ import print_function, unicode_literals

from config import CURRENCY_CACHE_NAME, CURRENCY_CACHE_AGE
from currency import fetch_currency_rates
from workflow import Workflow

log = None


def main(wf):
    # Insert delay to check info message is posted in Alfred
    # import time
    # time.sleep(10)
    wf.logger.debug('Fetching exchange rates from ECB ...')
    exchange_rates = wf.cached_data(CURRENCY_CACHE_NAME,
                                    fetch_currency_rates,
                                    CURRENCY_CACHE_AGE)
    wf.logger.debug('Exchange rates updated.')
    for currency, rate in exchange_rates.items():
        wf.logger.debug('1 EUR = {0} {1}'.format(rate, currency))


if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    wf.run(main)
