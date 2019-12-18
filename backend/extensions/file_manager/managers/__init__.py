#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports

# Pip package imports

# Internal package imports

DEFAULT_MANAGER = None

class BaseManager(object):

    def __init__(self, name, storage, *args, **kwargs):
        self.name = name
        self.storage = storage
