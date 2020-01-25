#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import locale

# Pip package imports
# Internal package imports


locale.setlocale(locale.LC_ALL, 'de_DE  ')

def format_price(value):
    if value == 0:
        return 'Free'
    return locale.currency(value, symbol=True, grouping=True)