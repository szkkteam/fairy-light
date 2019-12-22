#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import redirect, request, flash

from sqlalchemy.orm.base import manager_of_class, instance_state

from flask_admin.base import expose
from flask_admin.helpers import get_redirect_target
from flask_admin.babel import gettext

import flask_mm as mm

from loguru import logger

# Internal package imports
from backend.contrib.admin import ModelAdmin, macro
from backend.contrib.admin.field import MediaManagerImageUploadField
from backend.utils import string_to_bool
from backend.extensions.mediamanager import storage

from ..models import Image

class ImageAdmin(ModelAdmin):
    model = Image

    menu_icon_value = 'glyphicon-picture'

    create_template = 'admin/model/custom_upload_imgs_preview.html'

    can_create = True
    can_edit = True

    column_list = ('title', 'album', 'created_at', )
    column_labels = {'created_at': 'Date'}
    column_default_sort = ('created_at', True)

    column_details_list = ('title', 'created_at', 'updated_at')

    form_columns = ('album', 'path')

    form_extra_fields = {
        'path': MediaManagerImageUploadField('Image(s)', storage=storage.by_name('photo_album'))
    }


    """
    def create_model(self, form):
        try:
            model = self._manager.new_instance()
            # TODO: We need a better way to create model instances and stay compatible with
            # SQLAlchemy __init__() behavior
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
    """

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        from flask_admin.form import BaseForm, FormOpts, rules
        """
            Create model view
        """
        return_url = get_redirect_target() or self.get_url('.index_view')
        print("Return URL: ", return_url, flush=True)

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
                print("Model created: ", model, flush=True)
                flash(gettext('Record was successfully created.'), 'success')

                print("Request form: ", request.form, flush=True)

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
                           return_url=return_url)