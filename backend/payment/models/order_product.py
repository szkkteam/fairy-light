#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os

# Pip package imports
from flask_security.utils import hash_password as security_hash_password

# Internal package imports
from backend.database import (
    Column,
    BaseModel,
    String,
    Float,
    relationship,
    Boolean,
    foreign_key
)


class OrderProduct(BaseModel):

    product_id = foreign_key('Image', primary_key=True)
    product = relationship('Image') # Don't use backpopulate, because the image dosent have product_id column.

    order_id = foreign_key('Order', primary_key=True)
    order = relationship('Order', back_populates='order_product')

    __repr_props__ = ('id')
