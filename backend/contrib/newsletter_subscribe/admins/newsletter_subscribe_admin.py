#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
# Internal package imports
from backend.contrib.admin import ModelAdmin, macro

from ..models import NewsletterSubscribe


class NewsletterSubscribeAdmin(ModelAdmin):
    model = NewsletterSubscribe

    menu_icon_value = 'glyphicon-envelope'

    can_create = True
    can_edit = True

    column_list = ('email', 'is_active', 'created_at', )
    column_labels = {'created_at': 'Date'}
    column_default_sort = ('created_at', True)

    column_details_list = ('email', 'is_active', 'created_at', 'updated_at')

    column_formatters = {
        'email': macro('column_formatters.email'),
    }

