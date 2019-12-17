#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import redirect, request

from flask_admin.base import expose
from flask_admin.helpers import get_redirect_target

# Internal package imports
from backend.contrib.admin import ModelAdmin, macro
from backend.contrib.admin.form import MultiImageUploadForm
from backend.utils import string_to_bool

from ..models import Image

class ImageAdmin(ModelAdmin):
    model = Image

    menu_icon_value = 'glyphicon-picture'

    create_template = 'admin/model/custom_upload_imgs_preview.html'

    can_create = True
    can_edit = True

    column_list = ('title', 'is_public', 'created_at', )
    column_labels = {'created_at': 'Date'}
    column_default_sort = ('created_at', True)

    column_details_list = ('title', 'created_at', 'updated_at')

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        """
            Create model view
        """
        print("Form render", flush=True)

        return_url = get_redirect_target() or self.get_url('.index_view')
        if not self.can_create:
            return redirect(return_url)

        form = MultiImageUploadForm()
        if form.validate_on_submit():
            print("Form valid.", flush=True)

        if self.create_modal and request.args.get('modal'):
            template = self.create_modal_template
        else:
            template = self.create_template

        return self.render(template,
                           form=form,
                           form_opts=None,
                           return_url=return_url)