#!/usr/bin/python
# encoding: utf-8
#
# Copyright (c) 2017 Dean Jackson <deanishe@deanishe.net>
#
# MIT Licence. See http://opensource.org/licenses/MIT
#
# Created on 2017-07-16
#

"""Test converter."""

from __future__ import print_function, absolute_import

from collections import namedtuple
import logging

import pytest
from workflow import Workflow3

import convert
from defaults import Defaults

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()
convert.log = logging.getLogger('convert')


T = namedtuple('T', 'number dimensionality from_unit to_unit')
C = namedtuple('C', 'from_number from_unit to_number to_unit dimensionality')


def verify_parsed(t1, t2):
    """Verify results of `Converter.parse()`."""
    assert t1.number == t2.number
    assert t1.dimensionality == t2.dimensionality
    assert t1.from_unit == t2.from_unit
    assert t1.to_unit == t2.to_unit


def verify_conversion(c1, c2):
    """Verify results of `Converter.convert()`."""
    assert c1.from_number == c2.from_number
    assert c1.from_unit == c2.from_unit
    assert c1.to_number == c2.to_number
    assert c1.to_unit == c2.to_unit
    assert c1.dimensionality == c2.dimensionality


def test_invalid():
    """Test invalid input."""
    queries = [
        'dave',  # doesn't start with a number
        '1.3',  # no unit
        '5 daves',  # invalid units
        '10 km m cm',  # too many units
    ]
    c = convert.Converter(None)
    for query in queries:
        with pytest.raises(ValueError):
            c.parse(query)


def test_valid():
    """Test valid input."""
    data = [
        ('1.3 km', T(1.3, '[length]', 'kilometer', None)),
        ('1.3 km miles', T(1.3, '[length]', 'kilometer', 'mile')),
        ('5 m/s kph', T(5.0, '[length] / [time]', 'meter/second', 'kph')),
        ('21.3 m^2 acres', T(21.3, '[length] ** 2', u'meter²', 'acre')),
    ]
    c = convert.Converter(None)
    for t in data:
        i = c.parse(t[0])
        verify_parsed(t[1], i)


def test_conversion():
    """Test conversions."""
    data = [
        ('1km m', C(1, 'kilometer', 1000, 'meter', '[length]')),
    ]
    c = convert.Converter(None)
    for t in data:
        i = c.parse(t[0])
        res = c.convert(i)
        verify_conversion(t[1], res[0])


def test_defaults():
    """Test default conversions."""
    data = [
        ('1m', [
            C(1, 'meter', 100, 'centimeter', '[length]'),
            C(1, 'meter', 0.001, 'kilometer', '[length]')]),
        ('100g', [
            C(100, 'gram', 0.1, 'kilogram', '[mass]'),
            C(100, 'gram', 100000, 'milligram', '[mass]')]),
    ]

    wf = Workflow3()
    if 'default_units' not in wf.settings:
        wf.settings['default_units'] = {}

    wf.settings['default_units']['[length]'] = ['centimeter', 'kilometer']
    wf.settings['default_units']['[mass]'] = ['kilogram', 'milligram']

    c = convert.Converter(Defaults(wf))

    for t in data:
        i = c.parse(t[0])
        res = c.convert(i)
        assert len(res) == len(t[1])
        for j, r in enumerate(res):
            log.debug(r)
            verify_conversion(t[1][j], r)



if __name__ == '__main__':  # pragma: no cover
    pytest.main([__file__])
