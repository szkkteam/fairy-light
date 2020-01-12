#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
# Internal package imports
from backend.contrib.admin import ModelAdmin, macro
from backend.utils import string_to_bool

from ..models import Category

class CategoryAdmin(ModelAdmin):
    model = Category

    menu_icon_value = 'glyphicon-expand'

    can_create = True
    can_edit = True

    column_list = ('title', 'is_public', 'created_at', )
    column_labels = {'created_at': 'Date'}
    column_default_sort = ('created_at', True)

    column_details_list = ('title', 'is_public', 'slug', 'created_at', 'updated_at')

    column_formatters = {
        'email': macro('column_formatters.email'),
        #'preview': lambda view, context, model, name: model.get_preview(),
    }


