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
from ..models import StripeUser, Order

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
    print("KWARGS: ", kwargs, flush=True)
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

        return order

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

@payment.route('/checkout-webhook', methods=['POST'])
@csrf.exempt
def checkout_webhook():
    try:
        # The payment status should be checked here. If it's success, initiate the email sending with the digital product.
        request_data = request.get_json()
        # Get the secret key
        webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
        if webhook_secret:
            # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
            signature = request.headers.get('stripe-signature')
            try:
                event = stripe.Webhook.construct_event(
                    payload=request.data, sig_header=signature, secret=webhook_secret)
                data = event['data']
            except Exception as e:
                return e
            # Get the type of webhook event sent - used to check the status of PaymentIntents.
            event_type = event['type']
        else:
            data = request_data['data']
            event_type = request_data['type']
        data_object = data['object']

        print("data_object: ", data_object, flush=True)
        # If the user completed the checkout
        if event_type == 'checkout.session.completed':
            print("Success", flush=True)
            # data['object'] should contain the customer if it was created before
            print("Event data: ", data['object'], flush=True)

        return jsonify({'status': 'success'})

    except Exception as err:
        logger.error(traceback.format_exc())
        return abort(500)

"""
{
  "id": "ch_1G4CFiAbsp6t6e9Sh5JB5vOS",
  "object": "charge",
  "livemode": "",
  "payment_intent": "pi_1G4CExAbsp6t6e9SxO0arCha",
  "status": "succeeded",
  "amount": 2000,
  "amount_refunded": "",
  "application": "",
  "application_fee": "",
  "application_fee_amount": "",
  "balance_transaction": "txn_1G4CFjAbsp6t6e9SRmk2Jcs6",
  "billing_details": {
    "address": {
      "city": null,
      "country": null,
      "line1": null,
      "line2": null,
      "postal_code": "22222",
      "state": null
    },
    "email": "asd@asd.com",
    "name": "Mica",
    "phone": null
  },
  "captured": true,
  "created": 1579811170,
  "currency": "eur",
  "customer": "",
  "description": "Fairy Light ord. 12",
  "destination": "",
  "dispute": "",
  "disputed": "",
  "failure_code": "",
  "failure_message": "",
  "fraud_details": {
  },
  "invoice": "",
  "metadata": {
    "order_id": "12"
  },
  "on_behalf_of": "",
  "order": "",
  "outcome": {
    "network_status": "approved_by_network",
    "reason": null,
    "risk_level": "normal",
    "risk_score": 62,
    "seller_message": "Payment complete.",
    "type": "authorized"
  },
  "paid": true,
  "payment_method": "pm_1G4CFiAbsp6t6e9SGJ3InuVa",
  "payment_method_details": {
    "card": {
      "brand": "visa",
      "checks": {
        "address_line1_check": null,
        "address_postal_code_check": "pass",
        "cvc_check": "pass"
      },
      "country": "US",
      "exp_month": 2,
      "exp_year": 2022,
      "fingerprint": "s8Si8AUJ9BviRhgd",
      "funding": "credit",
      "installments": null,
      "last4": "4242",
      "network": "visa",
      "three_d_secure": null,
      "wallet": null
    },
    "type": "card"
  },
  "receipt_email": "",
  "receipt_number": "",
  "receipt_url": "https://pay.stripe.com/receipts/acct_1G3PV0Absp6t6e9S/ch_1G4CFiAbsp6t6e9Sh5JB5vOS/rcpt_GbP3j8mQAnleY82xlA9CJ9p2BzgeQYp",
  "refunded": "",
  "refunds": {
    "object": "list",
    "data": [
    ],
    "has_more": false,
    "total_count": 0,
    "url": "/v1/charges/ch_1G4CFiAbsp6t6e9Sh5JB5vOS/refunds"
  },
  "review": "",
  "shipping": "",
  "source": "",
  "source_transfer": "",
  "statement_descriptor": "",
  "statement_descriptor_suffix": "",
  "transfer_data": "",
  "transfer_group": ""
}
"""

@payment.route('/checkout-success', methods=['GET'])
def checkout_success():
    # Display the "Success" page
    pass

@payment.route('/checkout-cancel', methods=['GET'])
def checkout_cancel():
    # Display the "Cancel" page
    pass
