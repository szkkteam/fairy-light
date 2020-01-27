#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import current_app, render_template
from flask_mail import Message
from bs4 import BeautifulSoup

# Internal package imports
from backend.tasks import send_mail_async_task

def prepare_mail(subject, recipients, template, sender=None, **ctx):
    if not isinstance(recipients, (tuple, list)):
        recipients = [recipients]

    msg = Message(subject=subject, recipients=recipients, sender=sender)
    msg.html = render_template(template, **ctx)
    return msg

def send_mail(msg):
    if current_app and current_app.config.get('TESTING'):
        return send_mail_async_task.apply([msg])

    return send_mail_async_task.delay(msg)

def send_mail_sync(msg):
    if not msg.body:
        plain_text = '\n'.join(map(
            str.strip,
            BeautifulSoup(msg.html, 'lxml').text.splitlines()
        ))
        msg.body = re.sub(r'\n\n+', '\n\n', plain_text).strip()

    mail.send(msg)