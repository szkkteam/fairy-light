#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
# Internal package imports
from backend.magic import Bundle


shop_bundle = Bundle(__name__, blueprint_names=['shop', 'shop_lang', 'shop_api'])
