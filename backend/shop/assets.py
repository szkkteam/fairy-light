#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask_assets import AssetsBundle

# Internal package imports

css = AssetsBundle(
    'css/styles.css',
    'css/animations.css',
    __name__ + '/css/cart.css',
    __name__ + '/css/checkout.css',
    __name__ + '/css/shop.css',
    'css/responsive.css', # This should be the last
    output='build/shop.css',
    filters='cssmin')

js = AssetsBundle(
    __name__ + '/js/payment.js',
    output='build/shop.js',
    filters='jsmin')
