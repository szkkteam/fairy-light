#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
# Internal package imports
from backend.magic import Bundle
from backend.extensions.mediamanager import storage

shop_bundle = Bundle(__name__)

STORAGE_NAME = 'photo_album'

photo_album_storage = lambda : storage.by_name(STORAGE_NAME)