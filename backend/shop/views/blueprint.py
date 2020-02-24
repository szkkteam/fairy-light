#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import Blueprint, session, current_app

# Internal package imports

shop_lang = Blueprint('shop', __name__, url_prefix='/<lang_code>/shop',
                     template_folder='templates')
shop = Blueprint('shop', __name__, url_prefix='/shop',
                     template_folder='templates')

shop_api = Blueprint('shop_api', __name__, url_prefix='/shop-api',
                     template_folder='templates')

@shop.url_defaults
def add_language_code(endpoint, value):
    if 'lang_code' in values or not session.get('language'):
        session['language'] = value.get('lang_code')
        return
    if app.url_map.is_endpoint_expecting(endpoint, 'lang_code'):
        values['lang_code'] = session.get('language')

@shop.url_value_preprocessor
def pull_lang_code(endpoint, values):
    session['language'] = values.pop('lang_code', current_app.config.get('BABEL_DEFAULT_LOCALE'))