#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import re

# Pip package imports
from bs4 import BeautifulSoup

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

@celery.task(serializer='picke')
def prepare_product_async_task(order_id):
    try:
        order = create_archive(order_id)
        mail_data = prepare_mail(order=order)
    except Exception as e:
        # TOOD: What to do with exceptions?
        pass
