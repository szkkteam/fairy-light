#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os

# Pip package imports
from sqlalchemy.orm import relationship, remote, foreign

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


class Image(Model):

    path = Column(String(128), nullable=True)
    price = Column(Float, nullable=True)

    category_id = foreign_key('Category', nullable=True)
    category = relationship('Category', back_populates='images')

    __repr_props__ = ('id')

    @property
    def title(self):
        if self.path:
            return os.path.basename(photo_album_storage().namegen.original_name(self.path))
        return "No Image"

    @property
    def slug(self):
        return utils.slugify(self.title)

    def get_thumbnail_path(self):
        if not self.path:
            return ''
        return photo_album_storage().url(photo_album_storage().generate_thumbnail_name(self.path))

    def get_thumbnail_markup(self):
        if not self.path:
            return ''

        return Markup(
            '<img src="%s">' % self.get_thumbnail_path())