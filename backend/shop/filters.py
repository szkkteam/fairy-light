#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from babel.numbers import format_currency

# Internal package imports

def format_price(value, iso_locale='de_DE'):
    print("Value: ",value)
    if value == 0:
        return 'Free'
    return format_currency(value, 'EUR', format=u'¤ #,##0.00', locale=iso_locale)

def format_percentage(value, default=0.0):
    if not isinstance(value, float):
        try:
            value = float(value)
        except ValueError:
            value = default
    return format(value * 100, '.0f') + '%'
