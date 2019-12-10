#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
from datetime import date, datetime

# Pip package imports
from flask_admin.contrib.sqla import ModelView as BaseModelView
from flask_admin.consts import ICON_TYPE_GLYPH
from flask_admin.actions import action
import flask_excel as excel

# Internal package imports
from .form import ReorderableForm, CustomAdminConverter
from .macro import macro
from .security import AdminSecurityMixin


EXTEND_BASE_CLASS_ATTRIBUTES = (
    'column_formatters',
    'column_type_formatters',
)


class ModelAdmin(AdminSecurityMixin, BaseModelView):
    can_view_details = True

    menu_icon_type = ICON_TYPE_GLYPH
    menu_icon_value = None

    create_template = 'admin/model/base_create.html'
    details_template = 'admin/model/base_details.html'
    edit_template = 'admin/model/base_edit.html'
    list_template = 'admin/model/base_list.html'

    column_exclude_list = ('created_at', 'updated_at')
    form_excluded_columns = ('created_at', 'updated_at')

    column_type_formatters = {
        datetime: lambda view, dt: dt.strftime('%-m/%-d/%Y %-I:%M %p %Z'),
        date: lambda view, d: d.strftime('%-m/%-d/%Y'),
    }

    column_formatters = {
        'created_at': macro('column_formatters.datetime'),
        'updated_at': macro('column_formatters.datetime'),
    }

    form_base_class = ReorderableForm
    model_form_converter = CustomAdminConverter

    def __getattribute__(self, item):
        """Allow class attribute names in EXTEND_BASE_CLASS_ATTRIBUTES that are
        defined on subclasses to automatically extend the equivalently named
        attribute on this base class

        (a bit of an ugly hack, but hey, it's only the admin)
        """
        value = super().__getattribute__(item)
        if item in EXTEND_BASE_CLASS_ATTRIBUTES and value is not None:
            base_value = getattr(ModelAdmin, item)
            base_value.update(value)
            return base_value
        return value

    @action('export', 'Export')
    def action_export(self, ids):
        import pyexcel as pe
        query_sets = self.model.filter(self.model.id.in_(ids)).all()
        print("query_sets :", query_sets, flush=True)
        column_names = self.model.__table__.columns
        print("column_names :", column_names, flush=True)

        file_stream = pe.save_as(query_sets=query_sets, column_names=['id', 'email', 'is_active'],
                                 dest_file_type="csv")
        return (
            file_stream.read(),
            200,
            {
                'Content-Type': 'application/csv',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Expires': '0',
                'Content-Disposition': 'attachment; filename="mymodel.csv"'
            }
        )
