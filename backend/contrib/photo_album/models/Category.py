#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os

# Pip package imports
from sqlalchemy_mptt.mixins import BaseNestedSets

from sqlalchemy.orm import relationship, remote, foreign

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

from .Image import Image


class Category(Model, BaseNestedSets):

    title = Column(String(80), nullable=True)
    public = Column(Boolean(name='public'), default=True)
    price = Column(Float, nullable=True)

    images = relationship('Image', back_populates='category', cascade="all, delete, delete-orphan")

    __repr_props__ = ('id', 'title')

    @classmethod
    def get_images(cls, id):
        return Image.query.join(Category).filter(Image.category_id == id)
