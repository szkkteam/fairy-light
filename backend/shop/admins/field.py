#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from wtforms import Field, ValidationError, fields

try:
    from wtforms.fields.core import _unset_value as unset_value
except ImportError:
    from wtforms.utils import unset_value

from flask_admin.form import ImageUploadInput
from flask_admin.babel import gettext
from flask_admin._compat import urljoin, string_types
from flask_admin.helpers import get_url

from werkzeug.datastructures import FileStorage

import flask_mm as mm

# Internal package imports
from ..storage import get_protected, get_public


class StorageImageUploadField(fields.StringField):

    class StorageImageUploadInput(ImageUploadInput):
        """
            Renders a image input chooser field.
            You can customize `empty_template` and `data_template` members to customize
            look and feel.
        """
        empty_template = ('<input %(file)s>')

        def get_url(self, field):

            if field.thumbnail_size:
                filename = field.thumbnail_fn(field.data)
            else:
                filename = field.data

            return get_public().url(filename)

    widget = StorageImageUploadInput()

    def __init__(self, label=None, validators=None, **kwargs):

        assert isinstance(storage, mm.managers.BaseManager)

        self._should_delete = False

        super(StorageImageUploadField, self).__init__(label, validators, **kwargs)

    @property
    def thumbnail_size(self):
        return get_public().thumbnail_size

    @property
    def thumbnail_fn(self):
        return get_public().generate_thumbnail_name

    def is_file_allowed(self, filename):
        """
            Check if file extension is allowed.
            :param filename:
                File name to check
        """
        return get_public().is_allowed(filename)

    def _is_uploaded_file(self, data):
        retval = (data and isinstance(data, FileStorage) and data.filename)
        print("retval: ", retval ,flush=True)
        return retval

    def pre_validate(self, form):
        if self._is_uploaded_file(self.data) and not self.is_file_allowed(self.data.filename):
            raise ValidationError(gettext('Invalid file extension'))

        # Handle overwriting existing content
        if not self._is_uploaded_file(self.data):
            return

        # TODO: If overwrite alllowed?
        #if not self._allow_overwrite and os.path.exists(self._get_path(self.data.filename)):
        #    raise ValidationError(gettext('File "%s" already exists.' % self.data.filename))

    def process(self, formdata, data=unset_value):
        if formdata:
            marker = '_%s-delete' % self.name
            if marker in formdata:
                self._should_delete = True


        return super(MediaManagerImageUploadField, self).process(formdata, data)

    def process_formdata(self, valuelist):
        if self._should_delete:
            self.data = None
        elif valuelist:
            for data in valuelist:
                if self._is_uploaded_file(data):
                    self.data = data
                    break

    def populate_obj(self, obj, name):
        field = getattr(obj, name, None)
        if field:
            # If field should be deleted, clean it up
            if self._should_delete:
                get_public().delete(field)
                setattr(obj, name, None)
                return

        if self._is_uploaded_file(self.data):
            if field:
                get_public().delete(field)

            # Save first the thumbnail and the watermarked version.
            filename = get_public().save(self.data)

            print("filename: ", filename, flush=True)
            # update filename of FileStorage to our validated name
            self.data.filename = filename

            setattr(obj, name, filename)

    def generate_name(self, obj, file_data):
        return self.namegen(obj, file_data)


class ProtectedImageUploadField(fields.StringField):

    def __init__(self, label=None, validators=None, **kwargs):

        assert isinstance(storage, mm.managers.BaseManager)

        self._should_delete = False

        super(ProtectedImageUploadField, self).__init__(label, validators, **kwargs)

    def is_file_allowed(self, filename):
        """
            Check if file extension is allowed.
            :param filename:
                File name to check
        """
        is_allowed = get_public().is_allowed(filename) and get_protected().is_allowed(filename)
        return is_allowed

    def populate_obj(self, obj, name):
        field = getattr(obj, name, None)
        if field:
            # If field should be deleted, clean it up
            if self._should_delete:
                get_public().delete(field)
                get_protected().delete(field)
                setattr(obj, name, None)
                return

        if self._is_uploaded_file(self.data):
            if field:
                get_public().delete(field)
                get_protected().delete(field)

            # Save first the thumbnail and the watermarked version.
            filename = get_public().save(self.data)
            # Save the same image in high quality for the protected storage. Don't generate thumbnail, neither name for the image.
            get_protected().save(self.data, filename=filename, create_thumbnail=False, generate_name=False)
            print("filename: ", filename, flush=True)
            # update filename of FileStorage to our validated name
            self.data.filename = filename

            setattr(obj, name, filename)
