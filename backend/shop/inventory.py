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

from loguru import logger

# Internal package imports

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
    def add_item(cls, id, thumb, price, currency='eur', **kwargs):
        try:
            cls._prepare_layout()
            item = dict(
                id = id,
                thumb = thumb,
                price = price,
                currency = currency,
                **kwargs,
            )
            cls.storage['shoppingCart']['items'][id] = item
            logger.debug("Item \'{item}\' added to the storage.".format(item=item) )
        except Exception as e:
            logger.error(e)

    @classmethod
    def remove_item(cls, id):
        try:
            cls._prepare_layout()
            if id in cls.storage['shoppingCart']['items']:
                item = cls.storage['shoppingCart']['items'].pop(id)
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
        items = cls.storage['shoppingCart']['items']
        for key, item in items.items():
            total += item['price']

        return total

    @classmethod
    def get_num_of_items(cls):
        cls._prepare_layout()
        return len(cls.storage['shoppingCart']['items'].keys())

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


