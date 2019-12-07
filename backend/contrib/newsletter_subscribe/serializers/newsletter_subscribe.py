#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
# Internal package imports
from backend.api import ModelSerializer, fields

from ..models import NewsletterSubscribe

class NewsletterSubscribeSerializer(ModelSerializer):
    email = fields.Email(required=True)
    is_active = fields.Boolean(missing=True, allow_none=True)

    class Meta:
        model = NewsletterSubscribe
        exclude = ('created_at', 'updated_at')
        dump_only = ('is_active')

