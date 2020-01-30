#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import random
import string
import traceback
import sys
import enum

# Pip package imports
from flask import current_app, render_template, url_for, request, redirect, jsonify, abort, session
from flask.views import MethodView
from sqlalchemy import func

from loguru import logger

# Internal package imports
from backend.extensions import db

from .models import Category, Image

def get_image_details(currency, **kwargs):
    image = kwargs.get('image', None)
    if image is None:
        image_id = kwargs.get('image_id')
        image = Image.get(image_id)

    return {
        'id': image.id,
        'thumb': image.get_thumbnail_path(),
        'price': image.price if image.price else 0,
        'currency': currency
    }

class ProductInventory(object):
    """
        Layout:
            session = {
                'shoppingCart': {
                    'tracking': {
                        'orderId': <order id>,
                        'intentId: <stripe intent id>,
                    }
                    'items': {
                        '<album id>': {
                            'discount': <percentage float>,
                            'subTotal': <price int>,
                            'title': <title str>,
                            'products': {
                                '<image id>': {
                                    'id': <image id>,
                                    'thumb': <image thumbnail>,
                                    'price': <price int>,
                                    'currency': 'eur',
                                },
                                '<image id>': {
                                    'id': <image id>,
                                    'thumb': <image thumbnail>,
                                    'price': <price int>,
                                    'currency': 'eur',
                                },
                            }
                        }
                    }
                }
            }
    """

    # Temporary storage for items tracking
    storage = session

    @classmethod
    def _prepare_layout(cls):
        if 'shoppingCart' not in cls.storage:
            cls.storage['shoppingCart'] = {}
        if 'items' not in cls.storage['shoppingCart']:
            cls.storage['shoppingCart']['items'] = {}
        if 'tracking' not in cls.storage['shoppingCart']:
            cls.storage['shoppingCart']['tracking'] = {}

    @classmethod
    def _calculate_subtotal(cls, products):
        sum = 0
        for key, item in products.items():
            sum += item['price']
        return sum

    @classmethod
    def _calculate_discount(cls, category, products, discount_above=0.5):
        """
        Calculate the applied discount for the images. The equation should be the following.
        discount = max(x - (n/2),0)*(dc/(n/2))
        where:
        x - Number of images bought
        n - Total number of images in the album
        dc - Maximum discount for the album
        :param item:
        :return:
        """
        n = db.session.query(func.count(category.get_images().all()))
        n_2 = n*discount_above
        x = len(products.keys())
        dc = category.discount
        return max(x - (n_2), 0) * (dc / (n_2))

    @classmethod
    def add_item(cls, currency='eur', **kwargs):
        try:
            image = kwargs.get('image', None)
            if image is None:
                image_id = kwargs.get('image_id', None)
                image = Image.get(image_id)
            category = kwargs.get('category', None)
            if category is None:
                category = Category.get(image.category_id)
        except Exception as e:
            logger.error(e)
            raise
        else:
            try:
                cls._prepare_layout()
                category_item = {
                    'subTotal': 0,
                    'discount': 0,
                    'title': category.title,
                    'products': {

                    }
                }
                # Pop out the existing key, or get the default
                category_item = cls.storage['shoppingCart']['items'].pop(category.id, category_item)
                print(cls.storage['shoppingCart'], flush=True)
                # Convert image item layout
                image_item = get_image_details(image=image, currency=currency, **kwargs)
                # Calculate the subtotal
                category_item['subTotal'] = cls._calculate_subtotal(category_item['products'])
                # Calculate the discount
                category_item['discount'] = cls._calculate_discount(category, category_item['products'])
                # Re-insert category item
                category_item['products'][image.id] = image_item
                # Re-insert to session
                cls.storage['shoppingCart']['items'][category.id] = category_item

                print(cls.storage['shoppingCart'], flush=True)

                logger.debug("Item \'{item}\' added to the storage.".format(item=image_item) )
            except Exception as e:
                logger.error(e)

    @classmethod
    def add_category(cls, id, currency='eur', **kwargs):
        try:
            category = Category.get(id)
            images = Category.get_images(category.id).all()
            for image in images:
                cls.add_item(currency, image=image, category=category)

        except Exception as e:
            logger.error(e)

    @classmethod
    def remove_item(cls, id):
        try:
            image = Image.get(id)

            cls._prepare_layout()
            if image.category_id in cls.storage['shoppingCart']['items'] and\
                    id in cls.storage['shoppingCart']['items'][image.category_id]['products']:

                item = cls.storage['shoppingCart']['items'][image.category_id]['products'].pop(id)
                logger.debug("Item \'{item}\' removed from the storage.".format(item=item))
        except Exception as e:
            logger.error(e)

    @classmethod
    def clear(cls):
        try:
            cls._prepare_layout()
            cls.storage['shoppingCart'].pop('items')
            cls._prepare_layout()
            logger.debug("Storage cleared.")
        except Exception as e:
            logger.error(e)

    @classmethod
    def reset(cls):
        try:
            cls.storage.pop('shoppingCart')
            cls._prepare_layout()
            logger.debug("Storage has been resetted.")
        except Exception as e:
            logger.error(e)

    @classmethod
    def get_total_price(cls):
        total = 0
        cls._prepare_layout()
        categories = cls.storage['shoppingCart']['items']
        for category_id, category in categories.items():
            try:
                total += (category['subTotal'] * (1.0 - float(category['discount'])))
            except ValueError as e:
                logger.error(e)

        return total

    @classmethod
    def get_num_of_items(cls):
        num = 0
        cls._prepare_layout()
        categories = cls.storage['shoppingCart']['items']
        for category_id, category in categories.items():
            num += len(category['products'].keys())
        return  num

    @classmethod
    def get_content(cls):
        cls._prepare_layout()
        return cls.storage['shoppingCart']['items']

    @classmethod
    def get_order_id(cls):
        cls._prepare_layout()
        if 'orderId' in cls.storage['shoppingCart']['tracking']:
            return cls.storage['shoppingCart']['tracking']['orderId']
        return None

    @classmethod
    def get_intent_id(cls):
        cls._prepare_layout()
        if 'intentId' in cls.storage['shoppingCart']['tracking']:
            return cls.storage['shoppingCart']['tracking']['intentId']
        return None

    @classmethod
    def is_empty(cls):
        return (cls.get_num_of_items() == 0)

    @classmethod
    def set_order_id(cls, id):
        cls._prepare_layout()
        cls.storage['shoppingCart']['tracking']['orderId'] = id

    @classmethod
    def set_intent_id(cls, id):
        cls._prepare_layout()
        cls.storage['shoppingCart']['tracking']['intentId'] = id


