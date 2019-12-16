#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
# Internal package imports
from backend.database import (
    Column,
    Model,
    String,
    Boolean,
    relationship
)

from .image import Image

class Album(Model):
    title = Column(String(64))
    slug = Column(String(64))
    is_public = Column(Boolean(name='is_public'), default=True)

    images = relationship('Image', back_populates='album')

    __repr_props__ = ('id', 'title')

    @classmethod
    def get_publics(cls):
        return cls.query \
            .filter(cls.is_public==True) \
            .all()

    @classmethod
    def get_album_preview(cls, limit=4):
        return cls.query(Image).join(Album).filter(Image.album_id == cls.id).limit(limit)