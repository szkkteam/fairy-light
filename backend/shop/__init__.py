#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask_assets import AssetsBundle

# Internal package imports
from backend.magic import Bundle


shop_css = AssetsBundle(
    'css/styles.css',
    'css/animations.css',
    __name__ + '/css/cart.css',
    __name__ + '/css/checkout.css',
    __name__ + '/css/shop.css',
    'css/responsive.css', # This should be the last
    output='build/shop.css',
    filters='cssmin')

shop_js = AssetsBundle(
    __name__ + '/js/payment.js',
    output='build/shop.js',
    filters='jsmin')

shop_bundle = Bundle(__name__, assets={ 'shop_css': shop_css, 'shop_js': shop_js }, blueprint_names=['shop', 'shop_lang', 'shop_api'])
