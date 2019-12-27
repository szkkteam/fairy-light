#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
# Internal package imports
from backend.magic import Bundle
from backend.extensions.mediamanager import storage

photo_album = Bundle(__name__,
                     admin_icon_class='glyphicon glyphicon-picture',
                     admin_category_name='Photo Album')

STORAGE_NAME = 'photo_album'

photo_album_storage = lambda : storage.by_name(STORAGE_NAME)