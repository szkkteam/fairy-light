#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
# Internal package imports
from backend.extensions.mediamanager import storage

PUBLIC_STORAGE_NAME = 'photo'
PROTECTED_STORAGE_NAME = 'product'

public_storage = lambda : storage.by_name(PUBLIC_STORAGE_NAME)
protected_storage = lambda : storage.by_name(PROTECTED_STORAGE_NAME)

def get_public():
    return storage.by_name(PUBLIC_STORAGE_NAME)

def get_protected():
    return storage.by_name(PROTECTED_STORAGE_NAME)