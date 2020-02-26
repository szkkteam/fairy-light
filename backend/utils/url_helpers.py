#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import current_app, url_for

# Internal package imports

def safe_url_for_external(*args, **kwargs):
    base_url = kwargs.pop('_base_url', current_app.config.get('SERVER_NAME', 'localhost:5000'))
    print("Base url: ", base_url, flush=True)
    with current_app.app_context(), current_app.test_request_context(base_url=base_url):
        kwargs['_external'] = True
        return url_for(*args, **kwargs)
