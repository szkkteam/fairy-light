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

from .order_product import OrderProduct


class Order(Model):

    status = Column(String(20), nullable=False)

    order_product = relationship('OrderProduct', back_populates='order')
    product = association_proxy('order_product', 'product',
                               creator=lambda product: OrderProduct(product=product))

    __repr_props__ = ('id')


    def __init__(self, **kwargs):
        #products_ids = kwargs.pop('products_ids', None)
        products = kwargs.pop('products', None)
        if products:
            if isinstance(products, list):
                self.product.extend(products)
            else:
                self.product.append(products)
