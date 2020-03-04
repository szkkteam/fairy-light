#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
# Internal package imports
from backend.magic import Bundle


site_bundle = Bundle(__name__, assets_name='assets', blueprint_names=['site', 'site_lang'])
