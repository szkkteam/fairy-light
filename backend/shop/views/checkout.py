#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import random
import string
import traceback
import sys

# Pip package imports
from flask import current_app, make_response, render_template, url_for, request, redirect, jsonify, abort, session

from loguru import logger

import stripe

# Internal package imports
from backend.extensions import db
from backend.extensions import csrf

from .blueprint import shop
from ..models import StripeUser, Order, PaymentStatus
from ..webhook import StripeEvents, StripeWebhook

from ..inventory import ProductInventory
from ..models import Image

def is_intent_success():
    intent_id = ProductInventory.get_intent_id()
    if intent_id is not None:
        intent_obj = stripe.PaymentIntent.retrieve(intent_id)
        if 'charges' in intent_obj:
            data = intent_obj['charges']['data']
            if len(data) > 0:
                return bool(data[0]['status'] == 'succeeded')
    return False

def is_order_success():
    order_id = ProductInventory.get_order_id()
    if order_id is not None:
        order = Order.get(order_id)
        return bool(order.payment_status == PaymentStatus.confirmed)
    return False


def generate_password(size=8):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(size))

def get_stripe_public_key():
    return current_app.config['STRIPE_PUBLISHABLE_KEY']

def get_or_modify_intent(**kwargs):
    # Get or Create a PaymentIntent
    intent_id = ProductInventory.get_intent_id()
    if intent_id is not None:
        intent_obj = stripe.PaymentIntent.retrieve(intent_id)
        stripe.PaymentIntent.modify(intent_obj['id'],
            **kwargs)
        logger.debug("Payment Intent: \'{id}\' retrieved.".format(id=intent_obj['id']))
    else:
        intent_obj = stripe.PaymentIntent.create(**kwargs)
        ProductInventory.set_intent_id(intent_obj['id'])
        logger.debug("Payment Intent: \'{id}\' created.".format(id=intent_obj['id']))
    return intent_obj

def get_or_create_order(**kwargs):

    order_id = ProductInventory.get_order_id()
    if order_id is not None:
        order =  Order.get(order_id)
        logger.debug("Order: \'{id}\' retrieved.".format(id=order.id))
    else:
        order = Order.create(commit=False, **kwargs)
        # Must commit immidiatly because we need the assigned ID
        db.session.add(order)
        db.session.commit()

        ProductInventory.set_order_id(order.id)
        logger.debug("Order: \'{id}\' created.".format(id=order.id))

    return order

def get_or_create_user(**kwargs):
    email = kwargs.get('email', None)
    name = kwargs.get('name', 'Guest')
    user = StripeUser.get_by(email=email)
    if user is None:
        user = StripeUser(email=email, name=name)
        logger.debug("User: \'{user}\' created.".format(user=user))
    return user

@shop.route('/checkout/success')
def checkout_success():
    resp =  make_response(render_template('website/checkout/checkout_success.html'))
    resp.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
    return resp

@shop.route('/checkout/processing')
def checkout_processing():
    resp = make_response(render_template('website/checkout/checkout_processing.html'))
    resp.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
    return resp

@shop.route('/checkout/failed')
def checkout_failed():
    resp = make_response(render_template('website/checkout/checkout_failed.html'))
    resp.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
    return resp

#@payment.route('/')
@shop.route('/checkout', methods=['GET', 'POST'])
@csrf.exempt
def checkout():
    # If the cart's total price is 0 it means the customer selected only free products.
    # 1) Skipp the stripe payment process and redirect to the final page (Pro: Fast and customers don't has to provide card details. Cont: No tracking and billing receipes)
    # 2) NOT WORKING Still use the stripe payment process, but charge it with 0. (Pro: We have track, and they have receipe. Cont: It's a bit strange to put card details to something which is free)

    # Get the cart content
    total_price = ProductInventory.get_total_price()
    product_ids = list(ProductInventory.get_products().keys())

    order = get_or_create_order(products=product_ids)
    try:
        intent_obj = get_or_modify_intent(
            # Calculate the charge amount. The currency in the smallest currency unit (e.g., 100 cents to charge $1.00 or 100 to charge ¥100, a zero-decimal currency).
            amount=int(total_price * 100),
            description="Fairy Light ord. %d" % order.id,
            currency='eur',
            payment_method_types=['card'],
            metadata={'order_id': order.id},
        )
    except Exception as e:
        logger.error(e)
        logger.info("Order id: ", order.id)
        logger.info("Order payment status: ",order.payment_status)
        logger.info("Order shipping status: ", order.shipping_status)
        raise

    client_secret = intent_obj['client_secret']

    return render_template('website/checkout/checkout_modal.html',
                           #cart_items=cart_content,
                           client_secret=client_secret,
                           public_key=get_stripe_public_key(),
                           num_of_items=len(product_ids),
                           price_amount=total_price)

class PaymentWebhook(StripeWebhook):

    def _get_order(self, data):
        return Order.get(data['metadata']['order_id'])

    def handle_payment_intent_created(self, data):
        order = self._get_order(data)
        order.set_payment_status(PaymentStatus.requested)
        logger.debug("Payment Intent status: requested.")
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
        order.set_payment_status(PaymentStatus.confirmed, commit=False)

        logger.debug("Payment Intent status: confirmed.")

        db.session.add(user)
        db.session.add(order)
        db.session.commit()
        # TODO: Start the async process
        return self.return_success()

    def handle_payment_intent_failed(self, data):
        order = self._get_order(data)
        order.set_payment_status(PaymentStatus.error)
        logger.debug("Payment Intent status: failed.")
        return self.return_success()

    def handle_charge_succeeded(self, data):
        order = self._get_order(data)
        order.set_payment_status(PaymentStatus.confirmed, commit=False)
        logger.debug("Payment Charge status: confirmed.")

        try:
            name = data['billing_details']['name']
            email = data['billing_details']['email']
        except KeyError as err:
            logger.error(err)
        else:
            user = get_or_create_user(name=name, email=email)
            user.orders.append(order)
            db.session.add(user)

        db.session.add(order)
        db.session.commit()

        return self.return_success()

    def handle_charge_failed(self, data):
        order = self._get_order(data)
        order.set_payment_status(PaymentStatus.error)
        logger.debug("Payment Charge status: failed.")
        return self.return_success()

shop.add_url_rule('/checkout-webhook', view_func=PaymentWebhook.as_view('checkout_webhook'))