#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import render_template

# Internal package imports
from backend.site.views.blueprint import site

@site.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')


