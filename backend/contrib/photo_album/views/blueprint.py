#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import Blueprint

# Internal package imports

photo_album = Blueprint('photo_album', __name__, template_folder='templates')