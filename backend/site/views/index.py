#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import render_template

# Internal package imports
from .blueprint import site

@site.route('/')
@site.route('/index')
def index():
    return render_template('index.html')


