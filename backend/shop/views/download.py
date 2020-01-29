#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import io

# Pip package imports
from flask import render_template, request, url_for, redirect, abort, send_file

from sqlalchemy import asc

from loguru import logger
# Internal package imports
from backend.extensions import db
from backend.utils import decode_token
from backend.extensions.mediamanager import storage as mm

from .blueprint import shop
from ..models import Order
from ..inventory import ProductInventory
from .checkout import is_intent_success, is_order_success
from ..storage import get_protected


@shop.route('/download/<string:token>', methods=['GET'])
def product_download(token):
    try:
        order_id = decode_token(token)
        if order_id is None:
            # Requested token is invalid, or expired, or the Order is not found in the database
            logger.debug("Invalid token: \'{token}\' requested.".format(token=token))
            abort(404)
        # TODO: Using the passed storage name, or get it directly?
        st = get_protected()
        order = Order.get(order_id)
        # Read the zipfile as binary
        with open(st.path(order.path), 'rb') as arch_in:
            byte_stream = io.BytesIO(arch_in.read())

        byte_stream.seek(0)

        return send_file(
            byte_stream,
            #st.path(order.path),
            mimetype='application/zip',
            as_attachment=True,
            cache_timeout=1,
            attachment_filename='fairy_light_order_%s.zip' % order_id
        )

    except Exception as e:
        logger.error(e)
        return abort(404)
