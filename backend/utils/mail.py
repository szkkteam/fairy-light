#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import current_app, render_template
from flask_mail import Message

# Internal package imports
from backend.tasks import send_mail_async_task

def send_mail(subject, recipients, template, sender=None, **ctx):
    msg = prepare_send_mail(subject, recipients, template, sender, **ctx)

    if current_app and current_app.config.get('TESTING'):
        return send_mail_async_task.apply([msg])

    return send_mail_async_task.delay(msg)

def prepare_send_mail(subject, recipients, template, sender=None, **ctx):
    if not isinstance(recipients, (tuple, list)):
        recipients = [recipients]

    if sender is None:
        sender = current_app.config['MAIL_DEFAULT_SENDER']
        print("Sender: ", sender)
    msg = Message(subject=subject, recipients=recipients, sender=sender)
    msg.html = render_template(template, **ctx)

    return msg
