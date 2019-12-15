#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports

# Internal package imports
from backend.contrib.admin import FileAdmin
from backend.config import STATIC_FOLDER

class FileModelAdmin(FileAdmin):

    path = STATIC_FOLDER
    name = 'Test Admin'
