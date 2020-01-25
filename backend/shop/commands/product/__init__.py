#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os
import sys

# Pip package imports
import click
from flask.cli import with_appcontext

# Internal package imports
from backend.extensions.mediamanager import storage as mm
from backend.utils import listify

from backend.shop.models import ShippingStatus, Order, StripeUser, Image

from ..group import shop

#@click.option('--export', is_flag=True, default=False, expose_value=True,
#              help='Export the subscribers database to CSV file.')

@shop.command()
@click.option('--id', '-i', expose_value=True,
              help='Product ID to deliver.')
@click.option('--storage', '-s', help='Media Storage name to handle the files.')
@with_appcontext
def deliver(id, storage):
    st = mm.by_name(storage)

    order = Order.get(id)
    email = order.user.email
    # Mark progress as ongoing
    order.set_shipping_status(ShippingStatus.ongoing)
    #order.save(True)

    img_paths = []
    # Have to use order.product
    for image in order.product:
        print(image)
        print(image.id)
        #print(image.get_path())

    img_paths = [ st.path(image.path) for image in order.product ]
    print("Paths: ", img_paths)

    archive_path = st.archive_files(st.generate_name("product_%s.zip" % order.id), img_paths)
    # Store the archive path
    order.update(path=archive_path)

    order.save(True)
