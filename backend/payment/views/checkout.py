#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import current_app, render_template

from flask_wtf import FlaskForm
from wtform import StringField, SubmitField, validators

# Internal package imports
from .blueprint import payment

from backend.contrib.photo_album.views.cart_management import get_total_price()

def get_stripe_public_key():
    return current_app.config['STRIPE_PUBLISHABLE_KEY']

class PaymentForm(flaskForm):
    # Email field
    email = StringField('Email', validators=[validators.DataRequired(), validators.Email(), validators.Length(min=1, max=50)])



@payment.route('/')
@payment.route('/checkout')
def checkout():
    return render_template('checkout.html',
                           public_key=get_stripe_public_key(),
                           price_amount=get_total_price())
