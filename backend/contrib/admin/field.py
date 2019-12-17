#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from wtforms import Field

# Internal package imports
from .widget import ImagePreviewWidget

class ImagePreviewField(Field):
    widget = ImagePreviewWidget

    def __init__(self, *args, **kwargs):
        super(ImagePreviewField, self).__init__(*args, **kwargs)