#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os
# Pip package imports
from flask import session, url_for
from flask_babelex import lazy_gettext as _l
from flask_babelex import gettext as _g

# Internal package imports
FACEBOOK_LOCALE_CONST = {
    'hu': '_HU',
    'de': '_DE',
    'en': '_GB'
}

def get_facebook_meta(**kwargs):
    locale = session['language']
    if locale:
        # Convert locale to language_REGION code
        locale = locale + FACEBOOK_LOCALE_CONST[FACEBOOK_LOCALE_CONST]
    else:
        locale = 'en_GB' # Default locale
    data = dict(
        url=request.url,
        description=_g('social.facebook.description'),
        locale=locale,
        app_id=os.environ.get('FACEBOOK_APP_ID', ""),
        thumbnail=url_for('static', filename='site/img/facebook_thumb.jpg'), # Default facebook thumbnail
        thumbnail_width=1024, # In pixels
        thumbnail_height=768, # In pixels
        thumbnail_alt=_g('social.facebook.alt')
    )
    return { **data, **kwargs }

def get_twitter_meta(**kwargs):
    data = dict(
        summary=_g('social.twitter.summary'),
        account='@fairy.light', # TODO: Twitter account
        creator='@fairy.light', # TODO: Twitter account
        url=request.url,
        description=_g('social.twitter.description'),
        thumbnail=url_for('static', filename='site/img/twitter_thumb.jpg'),  # Default twitter thumbnail
    )
    return {**data, **kwargs}