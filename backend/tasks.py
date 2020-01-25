#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import re

# Pip package imports
from bs4 import BeautifulSoup

# Internal package imports
from backend.extensions.celery import celery
from backend.extensions.mail import mail
#from backend.extensions.mediamanager import storage

#from backend.payment.models import OrderStatus, Order, StripeUser
#from backend.contrib.photo_album.models import Image

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
def prepare_product_async_task(order_id, storage_name):


    pass