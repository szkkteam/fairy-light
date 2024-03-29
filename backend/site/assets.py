#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask_assets import Bundle as AssetsBundle

# Internal package imports

site = {
    # Site specific CSS files
    'vendor_css': AssetsBundle(
        'libs/bootstrap-4.4.1/css/bootstrap.css',
        'libs/bootstrap-select-1.13.9/css/bootstrap-select.css',
        'libs/magnific-popup-1.1.0/css/magnific-popup.css',
        'libs/venobox-1.8.6/css/venobox.css',
        output='build/css/site_vendor.min.css',
        filters='cssmin'
    ),
    # Vendor specific CSS files
    'css': AssetsBundle(
        'css/styles.css',
        'css/animations.css',
        'site/css/about.css',
        'site/css/index.css',
        'site/css/portfolio.css',
        'site/css/services.css',
        'css/responsive.css', # This should be the last
        output='build/css/site.min.css',
        filters='cssmin'
    ),
    # Vendor specific JS files
    'vendor_js': AssetsBundle(
        'libs/lazysizes-5.2.0/js/lazysizes.js',
        'libs/popper-1.16.0/js/popper.js',
        'libs/bootstrap-4.4.1/js/bootstrap.js',
        'libs/bootstrap-select-1.13.9/js/bootstrap-select.js',
        'libs/isotope-3.0.5/js/isotope.pkgd.js',
        'libs/magnific-popup-1.1.0/js/magnific-popup.js',
        'libs/scrolltofixed-1.0.8/js/jquery-scrolltofixed.js',
        'libs/venobox-1.8.6/js/venobox.js',
        output='build/js/site_vendor.min.js',
        filters='jsmin'
    ),
    # Site specific JS files
    'common_js': AssetsBundle(
        'js/app.js',
        'js/shopping_cart.js',
        output='build/js/site.min.js',
        filters='jsmin'
    ),
    # Site specific JS files
    'js': AssetsBundle(
        'site/js/cart.js',
        'site/js/portfolio.js',
        output='build/js/site_common.min.js',
        filters='jsmin'
    ),
}
