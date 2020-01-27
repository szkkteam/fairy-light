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
from ..models import Category, Order, PaymentStatus
from ..inventory import ProductInventory
from .checkout import is_intent_success, is_order_success
from .. import STORAGE_NAME


@shop.route('/download/<string:token>', methods=['GET'])
def product_download(token):
    try:
        order_id = decode_token(token)
        if order_id is None:
            # Requested token is invalid, or expired, or the Order is not found in the database
            logger.debug("Invalid token: \'{token}\' requested.".format(token=token))
            abort(404)
        # TODO: Using the passed storage name, or get it directly?
        st = m.by_name(STORAGE_NAME)
        # Read the zipfile as binary
        byte_stream = io.BytesIO()
        byte_stream = st.read(order.path)

        byte_stream.seek(0)

        return send_file(
            byte_stream,
            mimetype='application/zip',
            as_attachment=True,
            attachment_filename='order_%s.zip' % order_id
        )

    except Exception as e:
        logger.error(e)
