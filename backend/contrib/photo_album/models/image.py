#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os

# Pip package imports
from sqlalchemy.event import listens_for
from jinja2 import Markup

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
from .. import photo_album_storage

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
            return os.path.basename(photo_album_storage().namegen.original_name(self.path))
        return "No Image"

    @property
    def slug(self):
        return utils.slugify(self.title)

    def get_thumbnail(self):
        if not self.path:
            return ''

        return Markup(
            '<img src="%s">' % photo_album_storage().url(photo_album_storage().generate_thumbnail_name(self.path)))


@listens_for(Image, 'after_delete')
def del_image(mapper, connection, target):
    if target.path:
        # Delete image
        try:
            photo_album_storage().delete(target.path)
        except OSError:
            pass

    #return Markup('<img src="%s">' % photo_album_storage().url(photo_album_storage().generate_thumbnail_name(model.path)))