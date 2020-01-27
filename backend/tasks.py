#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import re

# Pip package imports


# Internal package imports
from backend.extensions.celery import celery
from backend.extensions.mail import mail
from shop.product import create_archive, deliver_product
from backend.utils import send_mail_sync


@celery.task(serializer='pickle')
def send_mail_async_task(msg):
    send_mail_sync(msg)

@celery.task(serializer='picke')
def prepare_product_async_task(order_id):
    try:
        order = create_archive(order_id)
        deliver_product_sync(order=order)
    except Exception as e:
        # TOOD: What to do with exceptions?
        pass
