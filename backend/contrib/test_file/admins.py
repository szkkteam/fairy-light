#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os.path as op

# Pip package imports
from flask import current_app

# Internal package imports
from backend.contrib.admin import FileAdmin

class FileModelAdmin(FileAdmin):

    path = op.join(op.dirname(__file__), 'static')
    url = 'static'
    name = 'Test Admin'