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
from flask_admin.form import FormOpts
from flask_admin.helpers import (get_form_data, validate_form_on_submit,
                                 get_redirect_target, flash_errors)

import flask_mm as mm

from requests.models import PreparedRequest

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


def get_root_id():
    root_id = request.args.get('root', None)
    if root_id is not None:
        return int(root_id)
    return root_id

def format_preview(view, context, model, name):
    # If the given model is Category, return with a link
    if isinstance(model, Category):
        # TODO: should return with a predefined image which is clickable (Folder like image)
        url = url_for('category.index_view', root=model.id)
        return Markup('<a href="%s" >%s</a>' % (url, model.title))
    # If the given model is Image, return with thumbnail
    elif isinstance(model, Image):
        return model.get_thumbnail_markup()

class PhotoAlbumAdmin(ModelAdmin):
    model = Category

    menu_icon_value = 'glyphicon-picture'

    can_create = True
    can_edit = True

    create_modal = True
    edit_modal = True

    create_modal_template = 'admin/model/modals/c_create.html'
    list_template = 'admin/model/c_list.html'

    #inline_models = (InlineImageAdmin(Image),)

    column_list = { 'preview', 'price' }

    form_columns = ( 'title', 'price')

    column_formatters = {
        # Two models will be passed for every formatter. Category and Image. Each formatter has to check for the model before returning a value
        'preview': format_title,

    }

    column_formatters_detail = {
        # Format images solution 2nd
        'image': format_images_field,
    }

    #form_columns = ( 'title', 'price')

    # To format how should the images displayed in list view, try with this solution: https://stackoverflow.com/questions/54721958/flask-admin-format-the-way-relationships-are-displayed

    def get_model_images(self):
        root_id = get_root_id()
        if not root_id:
            return []
        return self.model.get(root_id).get_images()


    def get_query(self):
        root_id = get_root_id()
        if not root_id:
            # Query Nodes which are root nodes (Default level = 1)
            return self.session.query(self.model).filter(self.model.level == self.model.get_default_level())
        else:
            root_node = self.model.get(root_id)
            # Get all the childrens for that given Node.
            category_list = root_node.get_children(self.session)
            # Get all images associated with that node
            images_list = root_node.get_images()
            # Return with a concatenated list
            return category_list + images_list

    """
    def get_count_query(self):
        root_id = request.args.get('root', None)
        if not root_id:
            return self.session.query(func.count('*')).select_from(self.model.query(self.model).filter(self.model.level() == self.model.get_default_level()))
        return self.session.query(func.count('*')).select_from(self.model.by(root_id).get_children(self.session))

    def get_one(self, id):
        return self.model.get(id)
    """

    def _get_breadcrumbs(self, root_id):
        breadcrumbs = []
        # Explicitly add the main root
        #breadcrumbs.append( {'url': url_for('category.index_view', root=None), 'title': 'Home' })
        if root_id is not None:
            ascendent_list = self.model.get(root_id).path_to_root(self.session, asc).all()
            print("ascendent_list: ", ascendent_list, flush=True)
            for ascendent in ascendent_list:
                breadcrumbs.append( {'url': url_for('category.index_view', root=ascendent.id), 'title': ascendent.title })

        print("Breadcrumbs: ", breadcrumbs, flush=True)
        return breadcrumbs

    @expose('/')
    def index_view(self):
        root_id = get_root_id()
        print("Root: ", root_id, flush=True)
        self._template_args['breadcrumbs'] = self._get_breadcrumbs(root_id)
        self._template_args['root_id'] = root_id
        return super(PhotoAlbumAdmin, self).index_view()

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        root_id = get_root_id()
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_create:
            return redirect(return_url)

        form = self.create_form()
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_create_rules, form=form)

        if self.validate_form(form):
            # in versions 1.1.0 and before, this returns a boolean
            # in later versions, this is the model itself
            model = self.create_model(form)
            if model:
                flash(gettext('Record was successfully created.'), 'success')
                if '_add_another' in request.form:
                    return redirect(request.url)
                elif '_continue_editing' in request.form:
                    # if we have a valid model, try to go to the edit view
                    if model is not True:
                        url = self.get_url('.edit_view', id=self.get_pk_value(model), url=return_url)
                    else:
                        url = return_url
                    return redirect(url)
                else:
                    # save button
                    return redirect(self.get_save_return_url(model, is_created=True))

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_create_rules)

        if self.create_modal and request.args.get('modal'):
            template = self.create_modal_template
        else:
            template = self.create_template

        return self.render(template,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url,
                           root_id=root_id)

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
            root_id = get_root_id()
            parent = self.model.get(root_id) if root_id else None
            print("Model create: root_id: ", root_id, flush=True)
            model = self.model(parent=parent)
            print("Model create: model: ", model, flush=True)
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