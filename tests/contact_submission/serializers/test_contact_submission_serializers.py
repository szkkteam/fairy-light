#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports

# Pip package imports
import pytest
from marshmallow.exceptions import ValidationError

# Internal package imports
from backend.contrib.contact_submission.serializers import ContactSubmissionSerializer

def test_contact_submission_serializer():
    serializer = ContactSubmissionSerializer()

    # check it escapes html tags, and converts paragraphs to html
    data = {'message': '<h1>hello</h1>\nworld'}
    msg = serializer.message_to_html(data)['message']
    assert '<h1>' not in msg, 'it should escape html from user-submitted messages'
    assert msg.count('<p>') == 2, 'it should wrap paragraphs in <p> tags'
    assert msg.count('</p>') == 2, 'it should wrap paragraphs in <p> tags'

    # check required fields
    with pytest.raises(ValidationError) as v:
        serializer.load({'name': None,
                         'email': None,
                         'message': None})

        assert 'Name is required.' in v.messages['name']
        assert 'Email is required.' in v.messages['email']
        assert 'Message is required.' in v.messages['message']

    # check email must be valid
    with pytest.raises(ValidationError) as v:
        serializer.load({'email': 'invalid'})
        assert 'Not a valid email address.' in v.messages['email']