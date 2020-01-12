#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
# Internal package imports
from backend.database import (
    Column,
    Model,
    String,
    Float,
    Boolean,
    relationship,
    foreign_key
)

from backend import utils

class Event(Model):
    title = Column(String(64))
    is_public = Column(Boolean(name='is_public'), default=True)
    price = Column(Float, nullable=True)

    albums = relationship('Album', back_populates='event', cascade="all, delete, delete-orphan")

    category_id = foreign_key('Category', nullable=True)
    category = relationship('Category', back_populates='events')

    __repr_props__ = ('id', 'title')

    @property
    def slug(self):
        return utils.slugify(self.title)

    @classmethod
    def get_publics(cls):
        return cls.query \
            .filter(cls.is_public == True) \
            .all()

