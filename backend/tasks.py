#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import re

# Pip package imports
from flask import current_app
from bs4 import BeautifulSoup
from loguru import logger

# Internal package imports
from backend.extensions.celery import celery
from backend.extensions.mail import mail
from backend.shop.product import create_archive, prepare_mail



@celery.task(serializer='pickle')
def send_mail_async_task(msg):
    if not msg.body:
        plain_text = '\n'.join(map(
            str.strip,
            BeautifulSoup(msg.html, 'lxml').text.splitlines()
        ))
        msg.body = re.sub(r'\n\n+', '\n\n', plain_text).strip()

    mail.send(msg)

@celery.task(serializer='pickle')
def prepare_product_async_task(order_id):
    from backend.utils.mail import prepare_send_mail
    try:
        order = create_archive(order_id)
        subject, recipients, template, kwargs = prepare_mail(order=order)
        # Send mail
        # TODO: This is a bit ugly but currently dont know how to render template outside of request context
        with current_app.test_request_context():
            msg = prepare_send_mail(subject, recipients, template, **kwargs)
            mail.send(msg)

        logger.debug("Order: \'{id}\' has been delivered to: \'{email}\' address.".format(id=order.id, email=recipients))
    except Exception as e:
        logger.error(e)
        raise
