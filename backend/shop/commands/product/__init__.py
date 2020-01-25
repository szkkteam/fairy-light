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
from backend.utils import listify
from backend.extensions import db

from backend.shop.models import ShippingStatus, Order, StripeUser, Image

from ..group import shop
from ...product import deliver_product, create_archive


@shop.command()
@click.option('--id', '-i', expose_value=True,
              help='Product ID to deliver.')
@click.option('--storage', '-s', help='Media Storage name to handle the files.')
@with_appcontext
def deliver(id, storage):
    order = create_archive(id, storage)
    deliver_product(order)

@shop.command()
@click.option('--id', '-i', expose_value=True,
              help='Product ID to deliver.')
@click.option('--storage', '-s', help='Media Storage name to handle the files.')
def archive(id, storage):
    create_archive(id, storage)

@shop.command()
@click.option('--id', '-i', expose_value=True,
              help='Product ID to deliver.')
def send(id):
    order = Order.get(id)
    # Check the order ID
    assert order, "Order Id: \'{id}\' is invalid.".format(id=id)
    deliver_product(order)

