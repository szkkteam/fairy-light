#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports

# Pip package imports

# Internal package imports
from . import BaseManager

class FileManager(BaseManager):

    def __init__(self, name, storage, *args, **kwargs):
        super(FileManager, self).__init__(name, storage, *args, **kwargs)

