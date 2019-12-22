#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os

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
from backend import utils
from backend.extensions.mediamanager import storage

class Image(Model):
    #title = Column(String(64), unique=True, nullable=False)
    #photo = ImageColumn(thumbnail_size=(250, 250, True), size=(1024, 1024, True))
    path = Column(String(128), nullable=True)
    #slug = Column(String(64))

    album_id = foreign_key('Album', nullable=True)
    album = relationship('Album', back_populates='images')

    __repr_props__ = ('id', 'path')

    @property
    def title(self):
        if self.path:
            return os.path.basename(storage.by_name('photo_album').namegen.original_name(self.path))
        return "No Image"

    @property
    def slug(self):
        return utils.slugify(self.title)
