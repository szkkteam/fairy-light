#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os

# Pip package imports
from flask_security.utils import hash_password as security_hash_password

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
from backend.contrib.photo_album import photo_album_storage
from backend import utils


class StripeUser(Model):

    email = Column(String(50), unique=True, index=True)
    name = Column(String(128))
    #password = Column(String, nullable=True)
    #stripe_token = Column(String(128), nullable=True)
    #stripe_customer_id = Column(String(255), nullable=True)

    orders = relationship('Order', back_populates='user')

    __repr_props__ = ('id')

    def __init__(self, hash_password=True, **kwargs):
        super().__init__(**kwargs)
        if 'password' in kwargs and hash_password:
            self.password = security_hash_password(kwargs['password'])
