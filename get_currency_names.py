#!/usr/local/bin/python
# encoding: utf-8
#
# Copyright © 2014 deanishe@deanishe.net
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2014-02-24
#

"""
Grab the abbreviations and names of currencies from the ECB website.

Not part of the workflow.
"""

from __future__ import print_function, unicode_literals

from pprint import pprint

from lxml.html import parse
from lxml.cssselect import CSSSelector

URL = 'http://www.ecb.europa.eu/stats/exchange/eurofxref/html/index.en.html'

rowsel = CSSSelector('div.forextable table tr')
cellsel = CSSSelector('td')

currencies = {}

for row in rowsel(parse(URL)):
    cells = cellsel(row)
    if len(cells) != 5:
        continue
    abbr, name = [c.text_content().strip() for c in cells[:2]]
    currencies[abbr] = name

pprint(currencies, indent=4)
