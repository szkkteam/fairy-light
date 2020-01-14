#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os

# Pip package imports
from sqlalchemy.orm import relationship, remote, foreign
from sqlalchemy.event import listens_for
from jinja2 import Markup

# Internal package imports
from backend.database import (
    Column,
    TreeModel,
    String,
    Float,
    relationship,
    ImageColumn,
    foreign_key
)
from backend.extensions import db
from backend import utils
from .. import photo_album_storage



class Node(TreeModel):
    title = Column(String, nullable=True)

    # Each node could have a price or an image.
    image = Column(String(128), nullable=True)
    price = Column(Float, nullable=True)

    __repr_props__ = ('id', 'path')
