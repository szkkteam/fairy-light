#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
# Internal package imports
from backend.magic import Bundle

from .admins import FileModelAdmin

test_bundle = Bundle(__name__,
                     admin_icon_class='glyphicon glyphicon-hdd',
                     admin_category_name='Test')
