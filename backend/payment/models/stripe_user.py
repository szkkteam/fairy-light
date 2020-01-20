#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os

# Pip package imports
from sqlalchemy.event import listens_for

from jinja2 import Markup

# Internal package imports
from backend.database import (
    Column,
    Model,
    String,
    Float,
    relationship,
    Boolean,
    foreign_key
)
from backend.contrib.photo_album import photo_album_storage
from backend import utils


class StripeUser(Model):

    token = Column(String(128), nullable=True)
    email = Column(String(50), unique=True, index=True)

    __repr_props__ = ('id')
