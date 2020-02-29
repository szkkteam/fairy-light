#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os

# Pip package imports
from flask import current_app

from loguru import logger

# Internal package imports
from backend.extensions.mediamanager import storage as mm
from backend.extensions import db
from backend.utils import encode_token


from .models import ShippingStatus, Order
from .storage import get_protected

def create_archive(id):
    try:
        st = get_protected()
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
            # If archive not exists yet
            if not order.path:
                # Get the image paths
                img_paths = [ image.path for image in order.product ]
                logger.debug("Archiving: [{paths}].".format(paths=img_paths))
                # Archive files
                archive_path = st.archive_files(st.generate_name("product_%s.zip" % order.id), img_paths)
                order.update(path=archive_path)
                logger.debug("Order: \'{id}\' archiving finished.".format(id=order.id))
        except Exception as e:
            logger.error(e)
            order.set_shipping_status(ShippingStatus.failed, False)
            raise

        finally:
            db.session.add(order)
            db.session.commit()

        return order

def prepare_mail(**kwargs):
    from backend.utils.url_helpers import safe_url_for_external
    from backend.utils.mail import get_mail_static_content
    order = kwargs.get('order', None)
    if order is None:
        order = Order.get(kwargs.get('id'))
    try:
        # Get the e-mail address
        email = order.user.email
        # Generate the unique download url
        token = encode_token(order.id)
        external_url = safe_url_for_external('shop.product_download', token=token, _external=True)
        logger.warning("Url: %s" % external_url)

        subject = "Product delivery %s." % order.id
        template = 'email/generated_product_deliver.html'
        #template = 'email/product_deliver.html'

        mail_data = dict(order_id=order.id,
                         name=order.user.name,
                         download_link=external_url,
                         **get_mail_static_content(),
                  )

        order.set_shipping_status(ShippingStatus.succeeded, False)
        logger.debug("Order: \'{id}\' can be accessed at the following url: {url}".format(id=order.id, url=external_url))

        return subject, email, template, mail_data

    except Exception as e:
        logger.error(e)
        order.set_shipping_status(ShippingStatus.failed, False)
        raise

    finally:
        db.session.add(order)
        db.session.commit()


