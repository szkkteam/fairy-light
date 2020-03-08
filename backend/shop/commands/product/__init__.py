#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports

# Pip package imports
import click
from flask.cli import with_appcontext
from loguru import logger

# Internal package imports
from backend.tasks import prepare_product_async_task
from backend.utils.mail import send_mail

from ..group import shop
from backend.shop.product import prepare_mail, create_archive


@shop.command()
@click.option('--id', '-i', expose_value=True,
              help='Product ID to deliver.')
@click.option('--lang', '-l', expose_value=True, default='en',
              help='Preferred language for the email.')
@with_appcontext
def deliver(id, lang):
    prepare_product_async_task.delay(id, lang)

@shop.command()
@click.option('--id', '-i', expose_value=True,
              help='Product ID to deliver.')
@with_appcontext
def archive(id):
    create_archive(id)

@shop.command()
@click.option('--id', '-i', expose_value=True,
              help='Product ID to deliver.')
@click.option('--lang', '-l', expose_value=True, default='en',
              help='Preferred language for the email.')
@with_appcontext
def send(id, lang):
    # Check the order ID
    try:
        subject, recipients, template, kwargs = prepare_mail(id=id, lang=lang)
    except TypeError as e:
        logger.error(e)
    else:
        send_mail(subject, recipients, template, kwargs)
        logger.debug("Order: \'{id}\' has been delivered to: \'{email}\' address.".format(id=id, email=recipients))
