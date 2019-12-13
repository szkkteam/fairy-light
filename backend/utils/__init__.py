#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import re
import unicodedata

# Pip package imports
from flask_sqlalchemy.model import camel_to_snake_case
from loguru import logger

# Internal package imports
from .decorators import was_decorated_without_parenthesis
from .mail import send_mail

def slugify(string):
    string = re.sub(r'[^\w\s-]', '',
                    unicodedata.normalize('NFKD', string.strip()))
    return re.sub(r'[-\s]+', '-', string).lower()


def title_case(string):
    return camel_to_snake_case(string).replace('_', ' ').title()


def pluralize(name):
    if name.endswith('y'):
        # right replace 'y' with 'ies'
        return 'ies'.join(name.rsplit('y', 1))
    elif name.endswith('s'):
        return f'{name}es'
    return f'{name}s'


def string_to_bool(s):
    if isinstance(s, str):
        if s.lower() in [ 'true', 'yes', 'y', '1', 'ye', 't' ]:
            return True
        elif s.lower() in [ 'false', 'no', 'n', '0', 'f' ]:
            return False
    return s