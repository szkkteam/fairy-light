#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import traceback
import sys

# Pip package imports
from flask import render_template, request, make_response, redirect, abort, Response, jsonify, session
from flask.views import MethodView
from werkzeug.exceptions import BadRequest
from loguru import logger

# Internal package imports
from backend.extensions import db
from ..models import Category, Image, PaymentStatus, Order

from ..inventory import ProductInventory
from .blueprint import shop
from .checkout import is_intent_success, is_order_success


def try_close_cart():
    if is_intent_success() or is_order_success():
        ProductInventory.reset()
        return True
    else:
        order_id = ProductInventory.get_order_id()
        if order_id is not None:
            order = Order.get(order_id)
            if order.payment_status == PaymentStatus.confirmed:
                ProductInventory.reset()
                return True
    return False


@shop.route('/cart/detail')
def cart_detail():
    try_close_cart()
    resp = make_response(render_template('photos_cart.html',
                           cart_items=ProductInventory.get_content(),
                           total_price=ProductInventory.get_total_price(),
                           return_url=request.args.get('url')
                           ))
    resp.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
    return resp

@shop.route('/cart/detail/refresh')
def cart_detail_refresh():
    return render_template('cart_detail.html',
                           cart_items=ProductInventory.get_content(),
                           total_price=ProductInventory.get_total_price()
                           )


class CartApi(MethodView):

    def get(self):
        try:
            if (request.content_type.startswith('application/json')):
                return jsonify(dict(
                    cartItems=ProductInventory.get_content(),
                    totalPrice=ProductInventory.get_total_price(),
                    numOfItems=ProductInventory.get_num_of_items()
                ))
                return json.loads(data.decode("utf-8"))
            else:
                return render_template('cart_mini.html',
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

    def get(self, category_id):
        abort(404)

class CartItemApi(MethodView):

    def get(self, item_id):
        abort(404)

    def post(self, item_id):
        try:
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