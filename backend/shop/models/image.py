#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os
import enum

# Pip package imports
from sqlalchemy.event import listens_for
import PIL

from jinja2 import Markup

# Internal package imports
from backend.database import (
    Column,
    Model,
    String,
    Float,
    relationship,
    Boolean,
    foreign_key,
    Enum
)
from backend.extensions import db
from backend import utils
from ..storage import get_public, get_protected

class ImageStatus(enum.Enum):

    active = "Product visible in the shop"                  # Default status when the object is created.
    depricated = "Product is no longer available"          # Products is no longer available

class Image(Model):

    status = Column(Enum(ImageStatus), nullable=False, default=ImageStatus.active)

    path = Column(String(128), nullable=True)
    price = Column(Float, nullable=True)

    category_id = foreign_key('Category', nullable=True)
    category = relationship('Category', back_populates='images')

    __repr_props__ = ('id')

    @property
    def title(self):
        if self.path:
            return os.path.basename(get_public().namegen.original_name(self.path))
        return "No Image"

    @property
    def slug(self):
        return utils.slugify(self.title)

    @property
    def image_size(self):
        img_data = get_protected().path(self.path)
        im = PIL.Image.open(img_data)
        return im.size

    def set_status(self, status, commit=False):
        self.status = status
        self.save(commit)

    def get_thumbnail_path(self):
        if not self.path:
            return ''
        return get_public().url(get_public().generate_thumbnail_name(self.path))

    def get_thumbnail_markup(self, height=None):
        if not self.path:
            return None
        # Default image markup
        markup = '<img src="%s">' % self.get_thumbnail_path()
        if height is not None:
            markup = '<img src="%s" height=%s>' % (self.get_thumbnail_path(), height)

        return Markup(markup)

    def get_path(self):
        if not self.path:
            return ''
        return get_public().url(self.path)

    @classmethod
    def get_all_by_ids(cls, list_of_ids):
        return db.session.query(Image).filter(Image.id.in_(list_of_ids)).all()



@listens_for(Image, 'after_delete')
def del_image(mapper, connection, target):
    if target.path:
        # Delete image
        try:
            get_public().delete(target.path)
        except OSError:
            pass