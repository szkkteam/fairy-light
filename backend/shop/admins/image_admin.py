#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports

# Internal package imports
from backend.contrib.admin import ModelAdmin, macro

from ..models import Image
from ..formatters import enum_field

class ImageAdmin(ModelAdmin):
    model = Image

    menu_icon_value = 'glyphicon-picture'

    can_create = False
    can_edit = True
    can_delete = False

    edit_modal = True
    details_modal = True

    column_filters = ('category.title','category.public', 'price', 'status')
    column_list = ( 'title', 'preview', 'status', 'price', 'category.title' )

    column_editable_list = ('price',)

    column_details_list = ('image', 'title', 'status', 'price')

    form_columns= ('category', 'status', 'price')

    column_formatters = {
        'status': lambda v, c, m, n: enum_field(m.status),
        'preview': lambda v, c, m, n: m.get_thumbnail_markup(height='50')
    }

    column_formatters_detail = {
        'image': lambda v, c, m, n: m.get_thumbnail_markup()
    }
