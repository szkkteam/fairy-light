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
from .widget import ImagePreviewWidget

class ImagePreviewField(Field):
    widget = ImagePreviewWidget

    def __init__(self, *args, **kwargs):
        super(ImagePreviewField, self).__init__(*args, **kwargs)




class MediaManagerImageUploadField(fields.StringField):

    class MultipleImageUploadInput(ImageUploadInput):
        """
            Renders a image input chooser field.
            You can customize `empty_template` and `data_template` members to customize
            look and feel.
        """
        empty_template = ('<input %(file)s multiple>')

        def get_url(self, field):

            if field.thumbnail_size:
                filename = field.thumbnail_fn(field.data)
            else:
                filename = field.data

            return field.storage.url(filename)
            #return get_url(field.endpoint, mm=field.storage.name, filename=filename)

    widget = MultipleImageUploadInput()

    def __init__(self, label=None, validators=None, storage=None, **kwargs):

        assert isinstance(storage, mm.managers.BaseManager)
        self.storage = mm.by_name() if not storage else storage

        self._should_delete = False

        super(MediaManagerImageUploadField, self).__init__(label, validators, **kwargs)

    @property
    def thumbnail_size(self):
        return self.storage.thumbnail_size

    @property
    def thumbnail_fn(self):
        return self.storage.generate_thumbnail_name

    def is_file_allowed(self, filename):
        """
            Check if file extension is allowed.
            :param filename:
                File name to check
        """
        is_allowed = self.storage.is_allowed(filename)
        print("is_allowed: ", is_allowed, flush=True)
        return is_allowed

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
                self.storage.delete(field)
                setattr(obj, name, None)
                return

        if self._is_uploaded_file(self.data):
            if field:
                self.storage.delete(field)

            filename = self.storage.save(self.data)
            print("filename: ", filename, flush=True)
            # update filename of FileStorage to our validated name
            self.data.filename = filename

            setattr(obj, name, filename)

    def generate_name(self, obj, file_data):
        return self.namegen(obj, file_data)
