#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import Blueprint, session, current_app

# Internal package imports

shop_lang = Blueprint('shop_lang', __name__, url_prefix='/<lang_code>/shop',
                     template_folder='templates')
shop = Blueprint('shop', __name__, url_prefix='/shop',
                     template_folder='templates', static_folder='static', static_url_path='/static/shop')

shop_api = Blueprint('shop_api', __name__, url_prefix='/shop-api',
                     template_folder='templates')

@shop_lang.url_defaults
def add_language_code(endpoint, value):
    if 'lang_code' in value or not session.get('language'):
        session['language'] = value.get('lang_code')
        return
    value['lang_code'] = session.get('language')

@shop_lang.url_value_preprocessor
def pull_lang_code(endpoint, values):
    session['language'] = values.pop('lang_code', current_app.config.get('BABEL_DEFAULT_LOCALE'))