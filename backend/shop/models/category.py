#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os

# Pip package imports
from sqlalchemy_mptt.mixins import BaseNestedSets
from sqlalchemy.event import listens_for
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
from backend.extensions import db
from backend import utils

from .image import Image, ImageStatus
from ..storage import get_public


class Category(Model, BaseNestedSets):

    title = Column(String(80), nullable=True)
    public = Column(Boolean(name='public'), default=True)
    discount = Column(Float, nullable=True)

    cover = Column(String(128), nullable=True)

    images = relationship('Image', back_populates='category')

    __repr_props__ = ('id', 'title')

    def get_thumbnail_path(self):
        if not self.cover:
            return None
        return get_public().url(get_public().generate_thumbnail_name(self.cover))

    def get_thumbnail_markup(self, height=None):
        if not self.cover:
            return None
        # Default image markup
        markup = '<img src="%s">' % self.get_thumbnail_path()
        if height is not None:
            markup = '<img src="%s" height=%s>' % (self.get_thumbnail_path(), height)

        return Markup(markup)


    def get_path(self):
        if not self.cover:
            return None
        return get_public().url(self.cover)

    @classmethod
    def get_images(cls, id):
        return Image.query.join(Category).filter(Image.category_id == id, Image.status == ImageStatus.active)

    @classmethod
    def get_list_from_root(cls, root_id, only_public=False):
        if not root_id:
            # Query Nodes which are root nodes (Default level = 1)
            base_query = db.session.query(Category).filter(cls.level == cls.get_default_level(), cls.public)
        else:
            # Get all the childrens for that given Node.
            base_query = Category.get(root_id).get_children(db.session)
        if only_public:
            base_query = base_query.filter(cls.public == True)
        return base_query

    @classmethod
    def sum_images_price(cls, id):
        images = cls.get_images(id).all()
        if len(images) == 0:
            return None
        overall_price = 0
        for image in images:
            if image.price:
                overall_price =+ image.price
        return overall_price

@listens_for(Category, 'after_delete')
def del_image(mapper, connection, target):
    if target.cover:
        # Delete image
        try:
            get_public().delete(target.cover)
        except OSError:
            pass