#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import current_app, url_for
from itsdangerous import URLSafeSerializer, BadData

# Internal package imports


def decode_email_token(token):
    """ Decode the token to retrive the encoded email address """
    s = URLSafeSerializer(current_app.secret_key, salt=current_app.config['SECURITY_PASSWORD_SALT'])
    try:
        return s.loads(token)
    except BadData:
        return None

def encode_email_token(email):
    """ Encode an email address and return with the encoded token """
    s = URLSafeSerializer(current_app.secret_key, salt=current_app.config['SECURITY_PASSWORD_SALT'])
    return s.dumps(email)

def generate_resubscribe_link(email):
    token = encode_email_token(email)
    return url_for('newsletter_subscribe.resubscribe', token=token)

def generate_unsubscribe_link(email):
    token = encode_email_token(email)
    return url_for('newsletter_subscribe.unsubscribe', token=token)