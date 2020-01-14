#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os

# Pip package imports
from flask import redirect, request, url_for, flash

from sqlalchemy.orm.base import manager_of_class, instance_state

from flask_admin import form
from flask_admin.base import expose
from flask_admin.helpers import get_redirect_target
from flask_admin.babel import gettext

import flask_mm as mm

from loguru import logger

from jinja2 import Markup

# Internal package imports
from backend.contrib.admin import ModelAdmin, macro
from backend.contrib.admin.field import MediaManagerImageUploadField
from backend.utils import string_to_bool

from ..models import PhotoNode

from .. import photo_album_storage


class PhotoAlbumAdmin(ModelAdmin):
    model = PhotoNode

    menu_icon_value = 'glyphicon-picture'

    can_create = True
    can_edit = True

    create_modal = True
    edit_modal = True

    form_columns = ('parent', 'title', 'price')
    #form_columns = ( 'title', 'price')

    def create_model(self, form):
        """
            Create model from form.
            :param form:
                Form instance
        """
        try:
            model = self._manager.new_instance()
            state = instance_state(model)
            self._manager.dispatch.init(state, [], {})

            print("Form parent: ", form.parent.data, flush=True)
            form.populate_obj(model)
            print("Model parent: ", model.parent, flush=True)
            self.session.add(model)
            self._on_model_change(form, model, True)
            self.session.commit()
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(gettext('Failed to create record. %(error)s', error=str(ex)), 'error')
                logger.exception('Failed to create record.')

            self.session.rollback()

            return False
        else:
            self.after_model_change(form, model, True)

        return model

    def on_model_change(self, form, model, is_created=False):
        if not is_created:
            # Do not delete, just update the model
            pass
        model.__init__(parent=form.parent.data)

    """
    create_template = 'admin/model/custom_upload_imgs_preview.html'

    can_create = True
    can_edit = True

    column_list = ('title', 'preview', 'price', 'album', 'created_at', )

    column_labels = {'created_at': 'Date'}
    column_default_sort = ('created_at', True)

    column_details_list = ('title', 'album', 'created_at', 'updated_at')

    form_columns = ('album', 'price', 'path')

    column_formatters = {
        'price': macro('column_formatters.price'),
        'preview': lambda view, context, model, name: model.get_thumbnail(),
    }

    form_extra_fields = {
        'path': MediaManagerImageUploadField('Image(s)', storage=photo_album_storage()),
    }
    """