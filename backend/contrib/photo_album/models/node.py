#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os

# Pip package imports
from sqlalchemy.orm import relationship, remote, foreign
from sqlalchemy.event import listens_for
from sqlalchemy import func
from sqlalchemy import Index, Sequence
from sqlalchemy_utils import LtreeType, Ltree
from jinja2 import Markup

# Internal package imports
from backend.database import (
    Column,
    Model,
    String,
    Float,
    relationship,
    ImageColumn,
    foreign_key
)
from backend.extensions import db
from backend import utils
from .. import photo_album_storage

id_seq = Sequence('nodes_id_seq')

class Node(Model):
    title = Column(String, nullable=True)

    # Each node could have a price or an image.
    image = Column(String(128), nullable=True)
    price = Column(Float, nullable=True)

    # LTree path
    path = Column(LtreeType, nullable=False)
    parent = relationship(
        'Node',
        primaryjoin=remote(path) == foreign(func.subpath(path, 0, -1)),
        backref='children',
        viewonly=True,)

    def __init__(self, name, parent=None):
        _id = db.engine.execute(id_seq)
        self.id = _id
        self.name = name
        ltree_id = Ltree(str(_id))
        self.path = ltree_id if parent is None else parent.path + ltree_id

    __table_args__ = (
        Index('ix_nodes_path', path, postgresql_using="gist")),

    __repr_props__ = ('id', 'path')

