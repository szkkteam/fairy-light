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
    output='build/css/shop.min.css',
    filters='cssmin')

shop_js = AssetsBundle(
    'shop/js/social.js',
    'shop/js/shop.js',
    output='build/js/shop.min.js',
    filters='jsmin')

cart_js = AssetsBundle(
    'shop/js/payment.js',
    'shop/js/cart.js',
    output='build/js/cart.min.js',
    filters='jsmin')
