#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports

# Pip package imports
# Internal package imports

def enum_field(field):
    return '({status}) - {desc}'.format(status=field.name, desc=field.value)