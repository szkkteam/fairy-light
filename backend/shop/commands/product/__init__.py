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
from backend.tasks import prepare_product_async_task

from backend.shop.models import ShippingStatus, Order, StripeUser, Image

from ..group import shop
from ...product import deliver_product, create_archive


@shop.command()
@click.option('--id', '-i', expose_value=True,
              help='Product ID to deliver.')
@with_appcontext
def deliver(id):
    prepare_product_async_task.delay(id)

@shop.command()
@click.option('--id', '-i', expose_value=True,
              help='Product ID to deliver.')
def archive(id):
    create_archive(id)

@shop.command()
@click.option('--id', '-i', expose_value=True,
              help='Product ID to deliver.')
def send(id):
    # Check the order ID
    assert order, "Order Id: \'{id}\' is invalid.".format(id=id)
    deliver_product(id=id)

