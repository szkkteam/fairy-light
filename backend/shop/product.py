#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os
import sys

# Pip package imports
import click
from flask.cli import with_appcontext

from loguru import logger

# Internal package imports
from backend.extensions.mediamanager import storage as mm
from backend.extensions import db

from backend.shop.models import ShippingStatus, Order

def create_archive(id, storage):
    try:
        st = mm.by_name(storage)
    except KeyError as e:
        logger.error(e)
        raise
    else:
        order = Order.get(id)
        # Check the order ID
        assert order, "Order Id: \'{id}\' is invalid.".format(id=id)
        try:
            # Update the Shipping Status
            order.set_shipping_status(ShippingStatus.ongoing, False)
            # Get the image paths
            img_paths = [ st.path(image.path) for image in order.product ]
            logger.debug("Archiving: [{paths}].".format(paths=img_paths))
            # Archive files
            archive_path = st.archive_files(st.generate_name("product_%s.zip" % order.id), img_paths)
            order.update(path=archive_path)
            logger.debug("Order: \'{id}\' archiving finished.".format(id=order.id))

        except Exception as e:
            logger.error(e)
            order.set_shipping_status(ShippingStatus.failed, False)
        finally:
            db.session.add(order)
            db.session.commit()

        return order

def deliver_product(order):
    # Get the e-mail address
    email = order.user.mail
