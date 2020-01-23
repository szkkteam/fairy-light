#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os
import enum

# Pip package imports
from flask_security.utils import hash_password as security_hash_password

# Internal package imports
from backend.database import (
    Column,
    Model,
    Integer,
    Enum,
    relationship,
    association_proxy,
    foreign_key
)

from .order_product import OrderProduct
from backend.contrib.photo_album.models import Image

class OrderStatus(enum.Enum):
    created = 1             # Default status when the object is created.
    payment_requested = 2   # Payment requested by stripe. Confirmation is ongoing.
    payment_confirmed = 3   # Payment confirmed by stripe
    payment_error = 4       # Payment failed
    delivery_queued = 5     # Products are queued for delivery
    delivery_ongoing = 6    # Delivery is in progress
    delivery_succeed = 7    # Delivery successful.
    delivery_failed = 8     # Delivery failed
    ready_to_download = 9   # Product is ready for the user to download
    download_in_progress = 10 # User started the download procedure
    download_succeed = 11   # The download procedure finished successfully
    download_failed = 12    # The download procedure failed.

class Order(Model):

    status = Column(Enum(OrderStatus), nullable=False)
    download_cnt = Column(Integer, nullable=True)

    order_product = relationship('OrderProduct', back_populates='order')
    product = association_proxy('order_product', 'product',
                               creator=lambda product: OrderProduct(product=product))

    user_id = foreign_key('StripeUser', nullable=True)
    user = relationship('StripeUser', back_populates='orders')

    __repr_props__ = ('id', 'status')


    def __init__(self, **kwargs):
        #products_ids = kwargs.pop('products_ids', None)
        self.status = OrderStatus.created
        #self.download_cnt = 0
        products = kwargs.pop('products', None)
        if products:
            if isinstance(products, list):
                products = [ Image.get(id) for id in products]
                self.product.extend(products)
            else:
                self.product.append(Image.get(products))

        super(Order, self).__init__(**kwargs)
