#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import render_template, request, url_for, redirect, abort

from sqlalchemy import asc

from loguru import logger
# Internal package imports
from backend.extensions import db

from .blueprint import photo_album

from ..models import Category
from ..models import Image

from .cart_management import get_cart, get_cart_num_of_items, get_total_price

def get_breadcrumbs(root_id):
    breadcrumbs = []
    # Explicitly add the main root
    #breadcrumbs.append( {'url': url_for('category.index_view', root=None), 'title': 'Home' })
    if root_id is not None:
        ascendent_list = Category.get(root_id).path_to_root(db.session, asc).all()
        print("ascendent_list: ", ascendent_list, flush=True)
        for ascendent in ascendent_list:
            breadcrumbs.append( {'url': url_for('photo_album.index_view', root=ascendent.id), 'title': ascendent.title })

    print("Breadcrumbs: ", breadcrumbs, flush=True)
    return breadcrumbs


@photo_album.route('/')
@photo_album.route('/<int:root>')
def index_view(root=None):
    # Calculate the breadcrumbs relative to the current view
    breadcrumbs = get_breadcrumbs(root)

    # Query the models at given level.
    data = Category.get_list_from_root(root, only_public=True).all()

    if len(data) == 0:
        # If there are no sub categories, query the images.
        data = Category.get_images(root)

        return render_template('photos_images_listing.html',
                               # Navigation specific
                               breadcrumbs=breadcrumbs,

                               # Shopping cart
                               cart_items=get_cart(),
                               cart_num_of_items=get_cart_num_of_items(),
                               total_price = get_total_price(),

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
                               cart_items=get_cart(),
                               cart_num_of_items=get_cart_num_of_items(),
                               total_price=get_total_price(),

                               # Datamodel
                               data=data)


