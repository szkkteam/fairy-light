#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
# Internal package imports
from backend.contrib.newsletter_subscribe.utils import encode_email_token, decode_email_token

TEST_EMAIL = 'foobar@example.com'

def test_encode_email():
    token = encode_email_token(TEST_EMAIL)
    assert token is not None

def test_decode_email():
    token = encode_email_token(TEST_EMAIL)
    email = decode_email_token(token)
    assert email is not None
    assert email == TEST_EMAIL
