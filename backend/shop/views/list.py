#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os

# Pip package imports
from flask import render_template, request, url_for, current_app, abort

from sqlalchemy import asc

from loguru import logger
# Internal package imports
from backend.extensions import db
from backend.site.social import get_twitter_meta, get_facebook_meta

from .blueprint import shop, shop_lang
from ..models import Category, Order, PaymentStatus, Image
from ..inventory import ProductInventory
from .shopping_cart import try_close_cart


def get_breadcrumbs(root_id):
    breadcrumbs = []
    if root_id is not None:
        ascendent_list = Category.get(root_id).path_to_root(db.session, asc).all()
        print("ascendent_list: ", ascendent_list, flush=True)
        for ascendent in ascendent_list:
            breadcrumbs.append( {'url': url_for('shop.index_view', root=ascendent.id, slug=ascendent.slug), 'title': ascendent.title })

    print("Breadcrumbs: ", breadcrumbs, flush=True)
    return breadcrumbs

@shop.route('/category/<int:category_id>')
@shop_lang.route('/category/<int:category_id>')
def category_detail(category_id):
    return render_template('website/shop/album_modal.html',
                           data=category_detail(category_id))

@shop.route('/photo/<int:photo_id>')
@shop_lang.route('/photo/<int:photo_id>')
def image_lightbox(photo_id):
    element = Image.get(photo_id)
    category_title = request.args.get('category')
    data = dict(
        category_title=category_title,
        thumbnail=element.get_thumbnail_path(),
        title=element.title,
        size=element.image_size,
        discounted_price=element.price,
        url_add_to_cart=url_for('shop_api.cart_item_api', item_id=element.id),
        url_image=element.get_path(),
        url_facebook_share=url_for('shop.index_view', root=element.id, _external=True),
    )

    return render_template('website/shop/lightbox.html',
                           data=data,
                           current_url=url_for('shop.index_view', root=int(element.category_id))
                           )


@shop.route('/')
@shop.route('/<int:root>/<slug>')
@shop_lang.route('/')
@shop_lang.route('/<int:root>/<slug>')
def index_view(root=None, slug=''):
    # Calculate the breadcrumbs relative to the current view
    breadcrumbs = get_breadcrumbs(root)

    if len(breadcrumbs) > 1:
        previous_url = breadcrumbs[-2]['url']
    elif len(breadcrumbs) == 1:
        previous_url = url_for('shop.index_view')
    else:
        previous_url = None
    # TODO: There must be a better way, how to close the session cart
    try_close_cart()

    # Get the parent category for social links
    if root is not None:
        parent = Category.get(root)
        # Prepare facebook social data
        facebook = get_facebook_meta(
            thumbnail=parent.get_thumbnail_path(),
            thumbnail_width=253,
            thumbnail_height=200,
            title=parent.title,
            url=url_for('shop.index_view', root=root, slug=parent.slug, _external=True))

        # Prepare Twitter social data
        twitter = get_twitter_meta(
            url=url_for('shop.index_view', root=root, slug=parent.slug, _external=True),
            title=parent.title,
            thumbnail=parent.get_thumbnail_path())
    else:
        facebook = None
        twitter = None

    # Query the models at given level.
    data = Category.get_list_from_root(root, only_public=True).all()

    try:
        cart_items = ProductInventory.get_content()
        cart_num_of_items = ProductInventory.get_num_of_items()
        total_price = ProductInventory.get_total_price()
    except Exception as e:
        logger.error(e)
        cart_items = {}
        cart_num_of_items = 0
        total_price = 0

    if len(data) == 0:
        # If there are no sub categories, query the images.
        data = Category.get_images(root)

        return render_template('website/shop/photos.html',
                               # Navigation specific
                               breadcrumbs=breadcrumbs,
                               current_url=breadcrumbs[-1]['url'] if len(breadcrumbs) > 0 else url_for('shop.index_view'),
                               previous_url=previous_url,

                               # Social
                               facebook=facebook,
                               twitter=twitter,

                               # Shopping cart
                               cart_items=cart_items,
                               cart_num_of_items=cart_num_of_items,
                               total_price=total_price,

                               # Datamodel
                               data=image_data(data, category_title=breadcrumbs[-1]['title']))

    else:
        return render_template('website/shop/albums.html',
                               # Navigation specific
                               breadcrumbs=breadcrumbs,
                               current_url=breadcrumbs[-1]['url'] if len(breadcrumbs) > 0 else url_for('shop.index_view'),
                               previous_url=previous_url,

                               # Social
                               facebook=facebook,
                               facebook_app_id=os.environ.get('FACEBOOK_APP_ID', ""),

                               # Shopping cart
                               cart_items=cart_items,
                               cart_num_of_items=cart_num_of_items,
                               total_price=total_price,

                               # Datamodel
                               data=category_data(data))

def image_data(data, category_title=None, slug=""):
    list_data = []
    for element in data:

        list_data.append(dict(
            thumbnail=element.get_thumbnail_path(),
            title=element.title,
            discounted_price=element.price,
            url_add_to_cart=url_for('shop_api.cart_item_api', item_id=element.id),
            url_image=url_for('shop.image_lightbox', photo_id=element.id, category=category_title),
            #url_image=element.get_path(),
            url_external=url_for('shop.index_view', root=element.category_id, slug=slug, _external=True),
        ))
    return list_data

def category_detail(category_id):
    element = Category.get(category_id)
    # Get the original and discounted price recursivly
    original_price, discounted_price = element.recursive_sum_images_price()
    data = dict(
        original_price=original_price,
        discounted_price=discounted_price,
        url_add_to_cart = url_for('shop_api.cart_category_api', category_id=element.id),
        title=element.title,
        images=image_data(element.images, category_title=element.title, slug=element.slug)
    )
    return data

def category_data(data):
    list_data = []
    for element in data:
        # Determine if customer can buy the whole album
        can_buy = True if element.discount is not None else False
        if can_buy:
            # Get the original and discounted price recursivly
            original_price, discounted_price = element.recursive_sum_images_price()

            #url_add_to_cart = url_for('shop.cart_category_api', category_id=element.id)
            url_add_to_cart = url_for('shop.category_detail', category_id=element.id)
        else:
            original_price = 0
            discounted_price = 0
            url_add_to_cart = '#'

        list_data.append(dict(
            can_buy=can_buy,
            num_of_images=element.recursive_num_of_images(),
            thumbnail=element.get_thumbnail_path(),
            title=element.title,
            original_price=original_price,
            discounted_price=discounted_price,
            url_add_to_cart=url_add_to_cart,
            url_category=url_for('shop.index_view', root=element.id, slug=element.slug),
            url_external=url_for('shop.index_view', root=element.id, slug=element.slug, _external=True),
        ))
    return list_data

