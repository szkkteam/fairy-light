#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import Blueprint, session, current_app

# Internal package imports

site_lang = Blueprint('site_lang', __name__, url_prefix='/<lang_code>', template_folder='templates')
site = Blueprint('site', __name__, template_folder='templates')


@site_lang.url_defaults
def add_language_code(endpoint, value):
    print("Value: ", value, flush=True)
    if 'lang_code' in value or not session.get('language'):
        # TODO: Also store in session, or just serve this file?
        #session['language'] = value.get('lang_code')
        return
    value['lang_code'] = session.get('language')

@site_lang.url_value_preprocessor
def pull_lang_code(endpoint, values):
    session['language'] = values.pop('lang_code', current_app.config.get('BABEL_DEFAULT_LOCALE'))