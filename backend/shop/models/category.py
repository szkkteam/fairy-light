#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os

# Pip package imports
from sqlalchemy_mptt.mixins import BaseNestedSets
from sqlalchemy.event import listens_for
from sqlalchemy import func
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

    def recursive_num_of_images(self):
        json_data = self.drilldown_tree(db.session, json=True, json_fields=lambda node: {'num': len(node.images)})
        sum = 0
        def recursive_count(node, sum):
            if 'children' in node:
                for i in node['children']:
                    sum += recursive_count(i, sum)
            else:
                return node['num']
            return sum
        for data in json_data:
            sum += recursive_count(data, sum)
        return sum

    def recursive_sum_images_price(self):

        def node_price(node):
            price = node._sum_images_price()
            discount = node.discount if node.discount is not None else 0
            discounted_price = price * ( 1 - discount)
            return {'original': price, 'discounted': discounted_price }

        json_data = self.drilldown_tree(db.session, json=True, json_fields=node_price)
        original = 0
        discounted = 0
        def recursive_count(node):
            original = 0
            discounted = 0
            if 'children' in node:
                for i in node['children']:
                    o, d = recursive_count(i)
                    original += o
                    discounted += d
            else:
                return node['original'], node['discounted']
            return original, discounted
        for data in json_data:
            o, d = recursive_count(data)
            original += o
            discounted += d
        return original, discounted

    def _get_images(self):
        return Image.query.join(Category).filter(Image.category_id == self.id, Image.status == ImageStatus.active)

    def _sum_images_price(self):
        images = self._get_images().all()
        if len(images) == 0:
            return 0
        overall_price = 0
        for image in images:
            if image.price is not None:
                overall_price += image.price
        return overall_price

    def get_path(self):
        if not self.cover:
            return None
        return get_public().url(self.cover)

    @classmethod
    def get_images(cls, id):
        return cls.get(id)._get_images()

    @classmethod
    def get_num_if_images(cls, id):
        return db.session.query(func.count(Image.id)).join(Category.images).group_by(Category.id).filter(Category.id == id).all()[0][0]

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
        return cls.get(id)._sum_images_price()

@listens_for(Category, 'after_delete')
def del_image(mapper, connection, target):
    if target.cover:
        # Delete image
        try:
            get_public().delete(target.cover)
        except OSError:
            pass