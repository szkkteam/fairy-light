#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os
import sys

# Pip package imports
from flask import url_for
import click
from flask.cli import with_appcontext

from loguru import logger

# Internal package imports
from backend.extensions.mediamanager import storage as mm
from backend.extensions import db
from backend.utils import prepare_mail, encode_token, send_mail_sync, send_mail

from backend.shop.models import ShippingStatus, Order
from . import STORAGE_NAME


def create_archive(id):
    try:
        st = mm.by_name(STORAGE_NAME)
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

def deliver_product(**kwargs):
    order = kwargs.get('order', None)
    if order is None:
        order = order.get(kwargs.get('id'))
    try:
        # Get the e-mail address
        email = order.user.mail
        # Generate the unique download url
        token = encode_token(order.id)

        subject = "Product order: %s ready to download" % order.id
        send_mail(prepare_mail(subject,
                    email,
                    'email/product_deliver.html',
                    order_id=order.id,
                    download_link=url_for('shop.product_download', token=token),
                  ))

        order.set_shipping_status(ShippingStatus.succeeded, False)
        logger.debug("Order: \'{id}\' has been delivered to: \'{email}\' address.".format(id=order.id, email=email))
        logger.debug("Order: \'{id}\' can be accessed at the following url: {url}".format(id=order.id, url=url_for('shop.product_download', token=token)))

    except Exception as e:
        logger.error(e)
        order.set_shipping_status(ShippingStatus.failed, False)
    finally:
        db.session.add(order)
        db.session.commit()

def deliver_product_sync(**kwargs):
    order = kwargs.get('order', None)
    if order is None:
        order = order.get(kwargs.get('id'))
    try:
        # Get the e-mail address
        email = order.user.mail
        # Generate the unique download url
        token = encode_token(order.id)

        subject = "Product order: %s ready to download" % order.id
        msg = prepare_mail(subject,
                    email,
                    'email/product_deliver.html',
                    order_id=order.id,
                    download_link=url_for('shop.product_download', token=token),
                  )

        send_mail_sync(msg)

        order.set_shipping_status(ShippingStatus.succeeded, False)
        logger.debug("Order: \'{id}\' has been delivered to: \'{email}\' address.".format(id=order.id, email=email))
        logger.debug("Order: \'{id}\' can be accessed at the following url: {url}".format(id=order.id, url=url_for('shop.product_download', token=token)))

    except Exception as e:
        logger.error(e)
        order.set_shipping_status(ShippingStatus.failed, False)
    finally:
        db.session.add(order)
        db.session.commit()