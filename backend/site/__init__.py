#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask_assets import AssetsBundle

# Internal package imports
from backend.magic import Bundle

assets = {
    'vendor_css': AssetsBundle(
        'libs/bootstrap-4.4.1/css/bootstrap.css',
        'libs/bootstrap-select-1.13.9/css/bootstrap-select.css',
        'libs/font-awsome-4.7.0/css/font-awsome.css',
        'libs/venobox-1.8.6/css/venobox.css',
        output='build/css/site_vendor.css',
        filters='cssmin'),

    'site_css': AssetsBundle(
        'css/styles.css',
        'css/animations.css',
        __name__ + '/css/about.css',
        __name__ + '/css/index.css',
        __name__ + '/css/portfolio.css',
        __name__ + '/css/services.css',
        'css/responsive.css', # This should be the last
        output='build/site.css',
        filters='cssmin'),

    'vendor_js': AssetsBundle(
        'libs/bootstrap-4.4.1/js/bootstrap.js',
        'libs/bootstrap-select-1.13.9/js/bootstrap-select.js',
        'libs/isotope-3.0.5/js/isotope.pkgd.js',
        'libs/jquery-3.4.1/js/jquery.js',
        'libs/magnific-popup-1.1.0/js/magnific-popup.js',
        'libs/scrolltofixed-1.0.8/js/jquery-srolltofixed.js',
        'libs/venobox-1.8.6/js/venobox.js',
        output='build/site_vendor.js',
        filters='jsmin'),
}

site_bundle = Bundle(__name__, assets=assets, blueprint_names=['site', 'site_lang'])
