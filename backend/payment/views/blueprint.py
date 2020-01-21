#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import Blueprint

# Internal package imports

payment = Blueprint('payment', __name__, url_prefix='/payment',
                     template_folder='templates')
