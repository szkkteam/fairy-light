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
    Float,
    relationship,
    Boolean,
    foreign_key
)

class StripeUser(Model):

    email = Column(String(50), unique=True, index=True)
    name = Column(String(128))
    #password = Column(String, nullable=True)
    #stripe_token = Column(String(128), nullable=True)
    #stripe_customer_id = Column(String(255), nullable=True)

    orders = relationship('Order', back_populates='user')

    __repr_props__ = ('id', 'email')
