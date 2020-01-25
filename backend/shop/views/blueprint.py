#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import Blueprint

# Internal package imports

shop = Blueprint('shop', __name__, url_prefix='/shop',
                     template_folder='templates')
