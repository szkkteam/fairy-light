#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
# Internal package imports
from backend.database import (
    Column,
    Model,
    String,
    relationship,
    ImageColumn,
    foreign_key
)

class Image(Model):
    title = Column(String(64), unique=True, nullable=False)
    photo = ImageColumn(thumbnail_size=(250, 250, True), size=(1024, 1024, True))
    slug = Column(String(64))

    album_id = foreign_key('Album', nullable=True)
    album = relationship('Album', back_populates='images')

    __repr_props__ = ('id', 'title')

