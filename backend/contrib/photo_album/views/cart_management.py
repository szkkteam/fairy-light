#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import traceback
import sys

# Pip package imports
from flask import render_template, request, url_for, redirect, abort, Response, jsonify, session
from werkzeug.exceptions import BadRequest

from loguru import logger
# Internal package imports
from backend.extensions import db
from backend.contrib.photo_album.models import Category
from backend.contrib.photo_album.models import Image

from .blueprint import photo_album

def get_cart():
    if 'cart_items' in session:
        return session['cart_items']
    return {}

def add_photo_item(id):
    data = Image.get(id)
    if data is not None:

        item = {data.id: {'id': data.id, 'thumb': data.get_thumbnail_path(), 'price': data.price if data.price else 0 }}
        session.modified = True
        if 'cart_items' in session:
            if data.id not in session['cart_items']:
                session['cart_items'][data.id] = item.get(data.id)
            else:
                # Item already added. Not possible to add it again. Quantity is not supproted
                pass
        else:
            session['cart_items'] = item
    else:
        return abort(404)
    return item


def get_cart_num_of_items():
    if 'cart_items' in session:
        return len(session['cart_items'].keys())
    return 0


@photo_album.route('/cart/add', methods=['POST'])
def add_item_to_cart():
    try:
        if request.method == 'POST':
            try:
                json_data = request.get_json(silent=False)
            except BadRequest as e:
                logger.error(e)
                return abort(400)
            else:
                _id = int(json_data.get('id'))
                _type = json_data.get('type')

                if _type and _type == 'category':
                    data = Category.get(_id)
                    if data is not None:
                        items = {}
                        images = Category.get_images(_id).all()
                        for image in images:
                            items = {**items, **add_photo_item(image.id)}
                        return jsonify({'shopItems': get_cart_num_of_items()})

                elif _type and _type == 'image':
                    item = add_photo_item(_id)
                    return jsonify({'shopItems': get_cart_num_of_items()})
                else:
                    pass

            return abort(404)
    except Exception as err:
        logger.error(traceback.format_exc())
        return abort(500)

@photo_album.route('/cart/remove', methods=['DELETE'])
def remove_item_from_cart():
    pass

@photo_album.route('/cart', methods=['GET'])
def get_cart_content():
    pass

@photo_album.route('/cart/clear', methods=['POST'])
def clear_cart():
    pass
