#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
from xml.etree import ElementTree as ET

# Pip package imports
from jinja2 import Markup
from sqlalchemy.event import listens_for

# Internal package imports
from backend.database import (
    Column,
    Model,
    String,
    Boolean,
    relationship
)

from .image import Image
from backend import utils
from .. import photo_album_storage

class Album(Model):
    title = Column(String(64))
    is_public = Column(Boolean(name='is_public'), default=True)

    images = relationship('Image', back_populates='album', cascade="all, delete, delete-orphan")

    __repr_props__ = ('id', 'title')


    @property
    def slug(self):
        return utils.slugify(self.title)

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
    """
    TODO: Some fancy tiled image preview for albums
    def get_preview(self):
        if not self.images:
            return 'No Image'
    
        container_div = ET.Element('div', attrib={'class': 'container-fluid'})
    
    
        images = Album.get_album_preview(limit=4)
    
        container_div.append( ET.Element('div', attrib={'class': 'row'}) )
    
        for idx, image in enumerate(images):
            img_div = ET.Element('figure', attrib={'class': 'col-sm-2 no-gutters'})
            img_div.append(
                ET.Element('img', attrib={'class': 'img-fluid img-thumbnail', 'src': photo_album_storage().url(photo_album_storage().generate_thumbnail_name(image.path))})
            )
    
            container_div.append(img_div)
    
    
        return Markup(ET.tostring(container_div, encoding='unicode'))
    """