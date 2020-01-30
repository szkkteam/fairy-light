#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import traceback
import sys

# Pip package imports
from flask import render_template, request, url_for, redirect, abort, Response, jsonify, session
from flask.views import MethodView
from werkzeug.exceptions import BadRequest
from loguru import logger

# Internal package imports
from backend.extensions import db
from ..models import Category, Image, PaymentStatus, Order

from ..inventory import ProductInventory
from .blueprint import shop



class CartApi(MethodView):

    def get(self):
        try:
            return render_template('cart_details.html',
                                   cart_items=ProductInventory.get_content(),
                                   total_price=ProductInventory.get_total_price(),
                                   )
        except Exception as e:
            logger.error(traceback.format_exc())
            return abort(500)

    def delete(self):
        try:
            ProductInventory.clear()
            return jsonify({ 'shopItems': ProductInventory.get_num_of_items() })
        except Exception as e:
            logger.error(traceback.format_exc())
            return jsonify({'error': 'Unknown error occured.'}), 500

class CartCategoryApi(MethodView):

    def post(self, category_id):
        try:
            ProductInventory.add_category(category_id)
            return jsonify({'shopItems': ProductInventory.get_num_of_items()})

        except Exception as err:
            logger.error(traceback.format_exc())
            return jsonify({'error': 'Unknown error occured.'}), 500


class CartItemApi(MethodView):

    def get(self, item_id):
        pass

    def post(self, item_id):
        try:
            print("Item id: ", item_id, flush=True)
            ProductInventory.add_item(image_id=item_id)
            return jsonify({'shopItems': ProductInventory.get_num_of_items()})

        except Exception as err:
            logger.error(traceback.format_exc())
            return jsonify({'error': 'Unknown error occured.'}), 500

    def delete(self, item_id):
        try:
            ProductInventory.remove_item(item_id)
            return jsonify({'shopItems': ProductInventory.get_num_of_items()})
        except Exception as err:
            logger.error(traceback.format_exc())
            return jsonify({'error': 'Unknown error occured.'}), 500


shop.add_url_rule("/cart/", view_func=CartApi.as_view("cart_api"))
shop.add_url_rule("/cart/<int:item_id>", view_func=CartItemApi.as_view("cart_item_api"))
shop.add_url_rule("/cart/category/<int:category_id>", view_func=CartCategoryApi.as_view("cart_category_api"))