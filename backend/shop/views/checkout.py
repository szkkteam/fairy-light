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
from backend.tasks import prepare_product_async_task

from .blueprint import shop, shop_api, shop_lang
from ..models import StripeUser, Order, PaymentStatus
from ..webhook import StripeEvents, StripeWebhook

from ..inventory import ProductInventory

def is_intent_success():
    intent_id = ProductInventory.get_intent_id()
    if intent_id is not None:
        try:
            intent_obj = stripe.PaymentIntent.retrieve(intent_id)
        except Exception as e:
            logger.error(e)
            return False
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
@shop_lang.route('/checkout/success')
def checkout_success():
    ProductInventory.reset()
    resp =  make_response(render_template('website/checkout/checkout_success.html'))
    resp.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
    return resp

@shop.route('/checkout/processing')
@shop_lang.route('/checkout/processing')
def checkout_processing():
    resp = make_response(render_template('website/checkout/checkout_processing.html'))
    resp.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
    return resp

@shop.route('/checkout/failed')
@shop_lang.route('/checkout/failed')
def checkout_failed():
    resp = make_response(render_template('website/checkout/checkout_failed.html'))
    resp.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
    return resp

#@payment.route('/')
@shop.route('/checkout', methods=['GET', 'POST'])
@shop_lang.route('/checkout', methods=['GET', 'POST'])
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
            metadata={'order_id': order.id, 'lang': session.get('language')},
        )
    except Exception as e:
        logger.error(e)
        logger.info("Order id: ", order.id)
        logger.info("Order payment status: ",order.payment_status)
        logger.info("Order shipping status: ", order.shipping_status)
        client_secret = None
    else:
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

    def _get_lang(self, data):
        try:
            lang = data['charges']['data'][0]['metadata']['lang']
        except KeyError:
            try:
                lang = data['metadata']['lang']
            except Exception as e:
                logger.error(e)
                return 'en'
        return lang

    def _get_user(self, data):
        user = None
        name = None
        email = None
        try:
            # print(data['charges']['data'], flush=True)
            name = data['charges']['data'][0]['billing_details']['name']
            email = data['charges']['data'][0]['billing_details']['email']
        except Exception as e:
            try:
                name = data['billing_details']['name']
                email = data['billing_details']['email']
            except Exception as e:
                logger.error(traceback.format_exc())
                print(data, flush=True)
        if name and email:
            user = get_or_create_user(name=name, email=email)
        return user

    def _prepare_data(self, data, payment_status, commit=True):
        order = self._get_order(data)
        user = self._get_user(data)
        if user is None:
            logger.error('Billing details is missing.')
            return self.return_error('Billing details is missing.', 400)

        if user is None:
            logger.error('Billing details is missing.')
            return None, None

        user.orders.append(order)
        order.set_payment_status(payment_status, commit=False)

        db.session.add(user)
        db.session.add(order)
        if commit:
            db.session.commit()

        return order, user


    def handle_payment_intent_created(self, data):
        order = self._get_order(data)
        order.set_payment_status(PaymentStatus.requested)
        logger.debug("Payment Intent status: requested.")
        return self.return_success()

    def handle_payment_intent_succeeded(self, data):
        # Preapre the user and order data
        order, user = self._prepare_data(data, PaymentStatus.confirmed)
        lang = self._get_lang(data)
        if not order or not user:
            return self.return_error('Billing details is missing.', 400)
        logger.debug("Payment Intent status: confirmed.")

        # Deliver product
        prepare_product_async_task.delay(order.id, lang)

        return self.return_success()

    def handle_payment_intent_failed(self, data):
        # Preapre the user and order data
        order, user = self._prepare_data(data, PaymentStatus.error)
        lang = self._get_lang(data)
        if not order or not user:
            return self.return_error('Billing details is missing.', 400)
        logger.debug("Payment Intent status: failed.")
        # TODO: Send mail about failed.
        return self.return_success()

    def handle_charge_succeeded(self, data):
        # Preapre the user and order data
        order, user = self._prepare_data(data, PaymentStatus.confirmed)
        if not order or not user:
            return self.return_error('Billing details is missing.', 400)
        logger.debug("Payment Intent status: succeed.")
        return self.return_success()

    def handle_charge_failed(self, data):
        # Preapre the user and order data
        order, user = self._prepare_data(data, PaymentStatus.error)
        lang = self._get_lang(data)
        if not order or not user:
            return self.return_error('Billing details is missing.', 400)
        logger.debug("Payment Charge status: failed.")
        # TODO: Send mail about failed
        return self.return_success()

shop_api.add_url_rule('/checkout-webhook', view_func=PaymentWebhook.as_view('checkout_webhook'))