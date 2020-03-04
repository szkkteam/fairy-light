#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask_assets import Bundle as AssetsBundle

# Internal package imports

css = AssetsBundle(
    'css/styles.css',
    'css/animations.css',
    'shop/css/cart.css',
    'shop/css/checkout.css',
    'shop/css/shop.css',
    'css/responsive.css', # This should be the last
    output='build/css/shop.css',
    filters='cssmin')

js = AssetsBundle(
    'shop/js/payment.js',
    output='build/js/shop.js',
    filters='jsmin')
