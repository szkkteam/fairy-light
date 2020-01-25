#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import render_template, request, url_for, redirect, abort

from sqlalchemy import asc

from loguru import logger
# Internal package imports
from backend.extensions import db

from .blueprint import shop
from ..models import Category, Order, PaymentStatus
from ..inventory import ProductInventory
from .checkout import is_intent_success, is_order_success


def get_breadcrumbs(root_id):
    breadcrumbs = []
    if root_id is not None:
        ascendent_list = Category.get(root_id).path_to_root(db.session, asc).all()
        print("ascendent_list: ", ascendent_list, flush=True)
        for ascendent in ascendent_list:
            breadcrumbs.append( {'url': url_for('shop.index_view', root=ascendent.id), 'title': ascendent.title })

    print("Breadcrumbs: ", breadcrumbs, flush=True)
    return breadcrumbs


@shop.route('/')
@shop.route('/<int:root>')
def index_view(root=None):
    # Calculate the breadcrumbs relative to the current view
    breadcrumbs = get_breadcrumbs(root)

    # TODO: There must be a better way, how to close the session cart
    order_id = ProductInventory.get_order_id()
    if order_id is not None:
        order = Order.get(order_id)
        if order.payment_status == PaymentStatus.confirmed:
            ProductInventory.reset()
    if is_intent_success() or is_order_success():
        ProductInventory.reset()

    # Query the models at given level.
    data = Category.get_list_from_root(root, only_public=True).all()

    if len(data) == 0:
        # If there are no sub categories, query the images.
        data = Category.get_images(root)

        return render_template('photos_images_listing.html',
                               # Navigation specific
                               breadcrumbs=breadcrumbs,

                               # Shopping cart
                               cart_items=ProductInventory.get_content(),
                               cart_num_of_items=ProductInventory.get_num_of_items(),
                               total_price = ProductInventory.get_total_price(),

                               # Datamodel
                               data=data)

    else:
        for element in data:
            if element.price == 0:
                element.price = Category.sum_images_price(element.id)

        return render_template('photos_listing.html',
                               # Navigation specific
                               breadcrumbs=breadcrumbs,

                               # Shopping cart
                               cart_items=ProductInventory.get_content(),
                               cart_num_of_items=ProductInventory.get_num_of_items(),
                               total_price = ProductInventory.get_total_price(),

                               # Datamodel
                               data=data)


