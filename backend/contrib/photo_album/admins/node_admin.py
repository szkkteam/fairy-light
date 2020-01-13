#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os

# Pip package imports
from flask import redirect, request, url_for

from sqlalchemy.orm.base import manager_of_class, instance_state

from flask_admin import form
from flask_admin.base import expose
from flask_admin.helpers import get_redirect_target
from flask_admin.babel import gettext

from flask_breadcrumbs import register_breadcrumb, current_breadcrumbs

# Internal package imports
from backend.contrib.admin import ModelAdmin, macro
from backend.contrib.admin.views import admin
from backend.contrib.admin.field import MediaManagerImageUploadField
from backend.utils import string_to_bool

from ..models import Node
from .. import photo_album_storage


from flask_admin.form import Select2Widget
from flask_admin.contrib.sqla.fields import QuerySelectField
#from flask_admin.fields import QuerySelectField


"""
'album': QuerySelectField(
    label='Album',
    query_factory=lambda: Album.all(),
    widget=Select2Widget
)
"""


class NodeAdmin(ModelAdmin):
    model = Node

    menu_icon_value = 'glyphicon-picture'

    #create_template = 'admin/model/custom_upload_imgs_preview.html'
    list_template =  'admin/model/photo_list.html'

    can_create = True
    can_edit = True

    create_modal = True
    edit_modal = True

    column_list = ('title', 'preview', 'price', 'created_at', )

    column_labels = {'created_at': 'Date'}
    column_default_sort = ('created_at', True)

    column_details_list = ('title', 'created_at', 'updated_at')

    form_columns = ('price', 'path')

    column_formatters = {
        'price': macro('column_formatters.price'),
        #'preview': lambda view, context, model, name: model.get_thumbnail(),
    }

    form_extra_fields = {
        'path': MediaManagerImageUploadField('Image(s)', storage=photo_album_storage()),
    }

    @expose('/')
    @register_breadcrumb(admin, '.', 'Home')
    def index_view(self):
        return super(NodeAdmin, self).index_view()


    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        from flask_admin.form import BaseForm, FormOpts, rules
        from flask_admin.helpers import is_form_submitted
        from flask import jsonify
        """
            Create model view with JSON response
        """
        return_url = get_redirect_target() or self.get_url('.index_view')
        print("Return URL: ", return_url, flush=True)

        if not self.can_create:
            return redirect(return_url)

        form = self.create_form()
        if not hasattr(form, '_validated_ruleset') or not form._validated_ruleset:
            self._validate_form_instance(ruleset=self._form_create_rules, form=form)

        if is_form_submitted():

            if form.validate():
                # in versions 1.1.0 and before, this returns a boolean
                # in later versions, this is the model itself
                model = self.create_model(form)
                if model:
                    return jsonify({'status': 'success', 'error': form.errors})

                else:
                    return jsonify({'status': 'failed', 'error': form.errors})
            else:
                return jsonify({'status': 'failed', 'error': form.errors})

        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_create_rules)

        if self.create_modal and request.args.get('modal'):
            template = self.create_modal_template
        else:
            template = self.create_template

        return self.render(template,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)