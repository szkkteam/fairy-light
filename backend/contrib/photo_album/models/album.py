#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from jinja2 import Markup

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
        return Image.query.filter_by(album_id=cls.id).limit(limit).all()
#        return cls.query(Image).join(Album).filter(Image.album_id == cls.id).limit(limit)
    """
    def __repr__(self):
        return Markup("<img src=%s>" % self.get_album_preview(limit=1)[0].get_thumbnail())
        #return Markup("<H1>Cioca")
    """
