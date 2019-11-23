#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os
from datetime import timedelta

# Pip package imports
import redis
from appdirs import AppDirs

# Internal package imports
from backend.utils.date import utcnow

# Application name and directory setup
APP_NAME = 'flask-starter'
app_dirs = AppDirs(APP_NAME)
APP_CACHE_FOLDER = app_dirs.user_cache_dir
APP_DATA_FOLDER = app_dirs.user_data_dir

# Flask assets folder setup
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
TEMPLATE_FOLDER = os.path.join(PROJECT_ROOT, 'backend', 'templates')
STATIC_FOLDER = os.environ.get('FLASK_STATIC_FOLDER', os.path.join(PROJECT_ROOT, 'static'))

STATIC_URL_PATH = '/static' # serve asset files in static/ at /static/

