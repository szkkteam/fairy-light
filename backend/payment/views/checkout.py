#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import random
import string
import traceback
import sys

# Pip package imports
from flask import current_app, render_template, url_for, request, redirect, jsonify, abort, session

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, validators

from loguru import logger

import stripe

# Internal package imports
from .blueprint import payment
from ..models import StripeUser, Order, OrderStatus
from .webhook import StripeEvents, StripeWebhook

from backend.contrib.photo_album.views.cart_management import get_total_price, get_cart
from backend.contrib.photo_album.models import Image
from backend.extensions import db
from backend.extensions import csrf

def generate_password(size=8):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))

def get_stripe_public_key():
    return current_app.config['STRIPE_PUBLISHABLE_KEY']

def get_charge_amount(cart_content):
    charge_amount = get_total_price()
    charge_amount_safe = get_products_total_price(cart_content)
    if charge_amount != charge_amount_safe:
        logger.warning("During calculating the charge amount there was a missmatch. Cart total: %s - Calculated from models: %s" % (charge_amount, charge_amount_safe))
        return charge_amount_safe
    return charge_amount

def get_products_total_price(cart):
    price = 0
    ids = cart.keys()
    models = Image.get_all_by_ids(ids)
    for m in models:
        price += m.price if m.price is not None else 0
    return price

def cart_to_stripe_items(cart):
    stripe_line_items = []
    for key, item in cart.items():
        stripe_line_items.append({
                'name': 'photo', # TOOD: Represent the photo image with some name.
                'description': 'Maximum quality digital photo.',
                'image': [item['thumb']],
                'amount': item['price'],
                'currency': 'eur',
                'quantity': 1}
        )
    return stripe_line_items

def get_or_modify_intent(**kwargs):
    # Get or Create a PaymentIntent
    if 'intent_id' in session:
        intent_obj = stripe.PaymentIntent.retrieve(session['intent_id'])
        stripe.PaymentIntent.modify(intent_obj['id'],
            **kwargs)
    else:
        intent_obj = stripe.PaymentIntent.create(**kwargs)
        session['intent_id'] = intent_obj['id']
    return intent_obj

def get_or_create_order(**kwargs):
    if 'order_id' in session:
        return Order.get(session['order_id'])
    else:
        order = Order.create(commit=False, **kwargs)
        db.session.add(order)
        db.session.commit()

        session['order_id'] = order.id

        return order

def get_or_create_user(**kwargs):
    email = kwargs.get('email', None)
    name = kwargs.get('name', 'Guest')
    user = StripeUser.get_by(email=email)
    if user is None:
        user = StripeUser(email=email,
                          name=name)
    return user

class RegisterStripeUserForm(FlaskForm):
    name = StringField('Name', validators=[validators.DataRequired(), validators.Length(min=1, max=64)])
    #firstName = StringField('Name', validators=[validators.Length(min=1, max=64)])
    #lastName = StringField('Name', validators=[validators.Length(min=1, max=64)])
    email = StringField('Email', validators=[validators.DataRequired(), validators.Email(), validators.Length(min=1, max=50)])

    def validate(self):
        # Validate the form.
        super(RegisterStripeUserForm, self).validate()
        # FIXME: email and username is not validated. Hopefully we can match the user by hand.

    def register_to_stripe(self, user):
        customer = stripe.Customer.create(
            description=self.name.data,
            metadata={"customer_code": user.id}
        )
        # TODO: Shall we create a subsription or anything?
        return customer

    def get_or_create(self):
        user = StripeUser.get_by(email=self.email.data)
        if user in None:
            return self._create_user()
        return user

    def _create_user(self):
        # TODO: Generate password. Should be 8 char long
        password = generate_password()
        user = StripeUser(
            name=self.name.data,
            email=self.email.data,
            password=password)
        customer = self.register_to_stripe(user)
        user.stripe_customer_id = customer.id

        user.save()
        return user


#@payment.route('/')
@payment.route('/checkout', methods=['GET', 'POST'])
@csrf.exempt
def checkout():
    # If the cart's total price is 0 it means the customer selected only free products.
    # 1) Skipp the stripe payment process and redirect to the final page (Pro: Fast and customers don't has to provide card details. Cont: No tracking and billing receipes)
    # 2) Still use the stripe payment process, but charge it with 0. (Pro: We have track, and they have receipe. Cont: It's a bit strange to put card details to something which is free)
    form = RegisterStripeUserForm()

    print("Request data: ", request.form, flush=True)

    # Get the cart content
    cart_content = get_cart()
    # Calculate the charge amount. The currency in the smallest currency unit (e.g., 100 cents to charge $1.00 or 100 to charge ¥100, a zero-decimal currency).
    charge_amount = int(get_charge_amount(cart_content) * 100)
    product_ids = list(cart_content.keys())

    order = get_or_create_order(products=product_ids)

    intent_obj = get_or_modify_intent(
        amount=charge_amount,
        description="Fairy Light ord. %d" % order.id,
        currency='eur',
        payment_method_types=['card'],
        metadata={'order_id': order.id},
    )

    client_secret = intent_obj['client_secret']

    return render_template('checkout.html',
                           form=form,
                           cart_items=cart_content,
                           client_secret=client_secret,
                           public_key=get_stripe_public_key(),
                           price_amount=get_total_price())

class PaymentWebhook(StripeWebhook):

    def _get_order(self, data):
        return Order.get(data['metadata']['order_id'])

    def handle_payment_intent_created(self, data):
        order = self._get_order(data)
        order.set_status(OrderStatus.payment_requested)
        return self.return_success()

    def handle_payment_intent_succeeded(self, data):
        order = self._get_order(data)
        user = None
        try:
            # print(data['charges']['data'], flush=True)
            name = data['charges']['data'][0]['billing_details']['name']
            email = data['charges']['data'][0]['billing_details']['email']
        except Exception as e:
            logger.error(e)
        else:
            user = get_or_create_user(name=name, email=email)

        if user is None:
            logger.error('Billing details is missing.')
            return self.return_error('Billing details is missing.', 400)

        user.orders.append(order)
        order.set_status(OrderStatus.payment_confirmed)

        # TODO: Start the async process
        return self.return_success()

    def handle_payment_intent_failed(self, data):
        order = self._get_order(data)
        order.set_status(OrderStatus.payment_error)
        logger.error('Payment Intent failed')
        return self.return_success()

    def handle_charge_succeeded(self, data):
        order = self._get_order(data)
        order.set_status(OrderStatus.payment_confirmed)

        try:
            name = data['billing_details']['name']
            email = data['billing_details']['email']
        except KeyError as err:
            logger.error(err)
        else:
            user = get_or_create_user(name=name, email=email)
            user.orders.append(order)

        return self.return_success()

    def handle_charge_failed(self, data):
        order = self._get_order(data)
        order.set_status(OrderStatus.payment_error)
        return self.return_success()


@payment.route('/checkout-success', methods=['GET'])
def checkout_success():
    # Display the "Success" page
    return render_template('checkout_success.html')

@payment.route('/checkout-cancel', methods=['GET'])
def checkout_cancel():
    # Display the "Cancel" page
    pass

payment.add_url_rule('/checkout-webhook', view_func=PaymentWebhook.as_view('checkout_webhook'))