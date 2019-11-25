#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
# Internal package imports
from .celery import celery
from .clean import clean
from .db import db_cli, fixtures, drop, reset
from .lint import lint
from .shell import shell
from .urls import url, urls


EXISTING_EXTENSION_GROUPS = ['db_cli']
