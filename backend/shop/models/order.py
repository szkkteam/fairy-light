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
    foreign_key,
    String
)

from .order_product import OrderProduct
from .image import Image

class ShippingStatus(enum.Enum):

    created = "Object created"                  # Default status when the object is created.
    queued = "Product delivery queued"          # Products are queued for delivery
    ongoing = "Product delivery is ongoing"     # Delivery is in progress
    succeeded = "Product delivery succeeded"    # Delivery successful.
    failed = "Product delivery failed"          # Delivery failed

class PaymentStatus(enum.Enum):

    created = "Object created."             # Default status when the object is created.
    requested = "Payment requested"         # Payment requested by stripe. Confirmation is ongoing.
    confirmed = "Payment confirmed"         # Payment confirmed by stripe
    error = "Payment error"                 # Payment failed
    cancelled = "Payment cancelled"         # Payment failed

class Order(Model):

    shipping_status = Column(Enum(ShippingStatus), nullable=False)
    payment_status = Column(Enum(PaymentStatus), nullable=False)
    download_cnt = Column(Integer, nullable=True)

    order_product = relationship('OrderProduct', back_populates='order')
    product = association_proxy('order_product', 'product',
                               creator=lambda product: OrderProduct(product=product))

    path = Column(String(128), nullable=True)

    user_id = foreign_key('StripeUser', nullable=True)
    user = relationship('StripeUser', back_populates='orders')

    __repr_props__ = ('id', 'status')


    def __init__(self, **kwargs):
        #products_ids = kwargs.pop('products_ids', None)
        self.shipping_status = ShippingStatus.created
        self.payment_status = PaymentStatus.created
        #self.download_cnt = 0
        products = kwargs.pop('products', None)
        if products:
            if isinstance(products, list):
                products = [ Image.get(id) for id in products]
                self.product.extend(products)
            else:
                self.product.append(Image.get(products))

        super(Order, self).__init__(**kwargs)

    def set_shipping_status(self, status, commit=True):
        self.shipping_status = status
        self.save(commit)

    def set_payment_status(self, status, commit=True):
        self.payment_status = status
        self.save(commit)