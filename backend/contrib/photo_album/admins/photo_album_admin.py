#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os

# Pip package imports
from flask import redirect, request, url_for, flash

from sqlalchemy.orm.base import manager_of_class, instance_state
from sqlalchemy import asc, func

from flask_admin import form
from flask_admin.base import expose
from flask_admin.helpers import get_redirect_target
from flask_admin.babel import gettext
from flask_admin.model.form import InlineFormAdmin

import flask_mm as mm

from loguru import logger

from jinja2 import Markup

# Internal package imports
from backend.contrib.admin import ModelAdmin, macro
from backend.contrib.admin.field import MediaManagerImageUploadField
from backend.utils import string_to_bool

from ..models import Category, Image

from .. import photo_album_storage

class InlineImageAdmin(InlineFormAdmin):
    form_columns = ('price',)

    form_extra_fields = {
        'path': MediaManagerImageUploadField('Image(s)', storage=photo_album_storage()),
    }

def format_images_field(view, context, model, name):
    """ Two possibility:
        1) Determine if we are just listing the category from it's parent view (Check breadcrumbs?) and display only the first child as picture. Probably use 'context'
            You check for 'breadcrumb' key and check what is the last breadcrumb. If breadcrumb[-1].title == model.title and we have images associated, then gather and list them.
            With this method, you can setup the template to use row, col, card's and put the img thumbnail markup inside the specific place.
        2) Put this formatter only into the column_formatter_details attribute, in this way when the Category is checked as 'details view' the images will be listed there only (Preferred)
     """
    # Get all the images related to this parent
    images = model.get_images()
    # Create a list item with thumbnails
    html_string = '<ul class="category-list-images">'
    for image in images:
        html_string += '<li> {} </li>'.format(image.get_thumbnail_markup())
        html_string += '</ul>'
    return Markup(html_string)


class PhotoAlbumAdmin(ModelAdmin):
    model = Category

    menu_icon_value = 'glyphicon-picture'

    can_create = True
    can_edit = True

    create_modal = True
    edit_modal = True

    create_modal_template = 'admin/model/modals/c_create.html'

    #inline_models = (InlineImageAdmin(Image),)

    form_columns = ( 'title', 'price')

    column_formatters_detail = {
        # Format images solution 2nd
        'image': format_images_field,
    }

    #form_columns = ( 'title', 'price')

    # To format how should the images displayed in list view, try with this solution: https://stackoverflow.com/questions/54721958/flask-admin-format-the-way-relationships-are-displayed
    """
    def get_query(self):
        root_id = request.args.get('root', None)
        if not root_id:
            # Query Nodes which are root nodes (Default level = 1)
            return self.model.query(self.model).filter(self.model.level() == self.model.get_default_level())
        # Get all the childrens for that given Node.
        return self.model.by(root_id).get_children(self.session)

    def get_count_query(self):
        root_id = request.args.get('root', None)
        if not root_id:
            return self.session.query(func.count('*')).select_from(self.model.query(self.model).filter(self.model.level() == self.model.get_default_level()))
        return self.session.query(func.count('*')).select_from(self.model.by(root_id).get_children(self.session))

    def get_one(self, id):
        return self.model.by(id)

    def _get_breadcrumbs(self, root_id):
        breadcrumbs = []
        # Explicitly add the main root
        breadcrumbs.append((url_for('admin.index_view', root_id=None), 'Home'))
        if root_id is not None:
            ascendent_list = self.model.path_to_root(self.session).all(asc)
            for ascendent in ascendent_list:
                breadcrumbs.append((url_for('admin.index_view', root_id=ascendent.id), ascendent.title))
        return breadcrumbs
    """
    @expose('/')
    def index_view(self):
        root_id = request.args.get('root', None)
        print("Root: ", root_id, flush=True)
        #self._template_args['breadcrumbs'] = self._get_breadcrumbs(root_id)
        self._template_args['breadcrumbs'] = 'Im the breadcrumb'
        self._template_args['root_id'] = root_id
        return super(PhotoAlbumAdmin, self).index_view()

    # Adding the JS file to handle multiple image upload
    def render(self, template, **kwargs):
        """
        using extra js in render method allow use
        url_for that itself requires an app context
        """
        self.extra_js = [url_for("static", filename="js/form_upload_imgs_preview.js")]
        return super(PhotoAlbumAdmin, self).render(template, **kwargs)

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

            form.populate_obj(model)
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
        root_id = request.args.get('root', None)
        print("Root id: ", root_id, flush=True)
        model.__init__(parent_id=root_id)
        print("Model: ", model, flush=True)

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