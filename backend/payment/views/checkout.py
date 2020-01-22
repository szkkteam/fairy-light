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
from ..models import StripeUser

from backend.contrib.photo_album.views.cart_management import get_total_price, get_cart
from backend.contrib.photo_album.models import Image
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
        price += m.price
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

class RegisterStripeUserForm(FlaskForm):
    name = StringField('Name', validators=[validators.DataRequired(), validators.Length(min=1, max=64)])
    #firstName = StringField('Name', validators=[validators.Length(min=1, max=64)])
    #lastName = StringField('Name', validators=[validators.Length(min=1, max=64)])
    email = StringField('Email', validators=[validators.DataRequired(), validators.Email(), validators.Length(min=1, max=50)])
    # This will be filled out automatically by stripe
    stripeToken = PasswordField('Stripe Token', validators=[validators.DataRequired()])

    def validate(self):
        # Validate the form.
        super(RegisterStripeUserForm, self).validate()
        # FIXME: email and username is not validated. Hopefully we can match the user by hand.

    def register_to_stripe(self, user):
        customer = stripe.Customer.create(
            description=self.name.data,
            source=self.stripeToken.data,
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
            password=password,
            stripe_token=self.stripeToken.data)
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

    if form.validate_on_submit():

        print("Form data: ", form, flush=True)

        # TODO: Create the customer, based on from data
        #user = form.get_or_create()
        # Get the cart content
        cart_content = get_cart()
        # Calculate the charge amount. The currency in the smallest currency unit (e.g., 100 cents to charge $1.00 or 100 to charge ¥100, a zero-decimal currency).
        charge_amount = get_charge_amount(cart_content) * 100

        # TODO: Create an order model and assign the ID to the intent object

        # TODO: Implement imdopotency key to prevent double charges.
        # Eg: Put the Create function into a fallback retry with auto generated idempotency_key. So each time it will generate
        # a new key and retries it a few time.

        # Get or Create a PaymentIntent
        if 'intent_id' in session:
            intent_obj= stripe.PaymentIntent.retrieve(session['intent_id'])
        else:
            intent_obj = stripe.PaymentIntent.create(
                amount=charge_amount,
                currency='eur',
                # TODO: Check if this will be alway less than 22 char
                description="Fairy Light ord. %d" % 9999,
                receipt_email=user.email,
                customer=user.stripe_customer_id,
                payment_method_types=['card'],
                # TODO: Create an order model
                metadata={ 'user_id': user.id, 'order_id': 9999 },
            )
            session['intent_id'] = intent_obj['id']

        client_secret = intent_obj['client_secret']

        print("Session: ", session, flush=True)

        return render_template('checkout.html',
                               form=form,
                               session_id=client_secret,
                               public_key=get_stripe_public_key(),
                               price_amount=get_total_price())

    return render_template('checkout.html',
                           form=form,
                           public_key=get_stripe_public_key(),
                           price_amount=get_total_price())
    #return redirect(url_for('payment.checkout'))

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
        # If the user completed the checkout
        if event_type == 'checkout.session.completed':
            # data['object'] should contain the customer if it was created before
            customer_id = data['object']['customer']
            user = StripeUser.get_by(stripe_customer_id=customer_id)
            if user is None:
                # TODO: Send some error to somewhere if the user does not exists.
                pass
            email = user.email
            # TODO: Set the async task to create the zip file and send it to the customers. Also create a DB object??

        return jsonify({'status': 'success'})

    except Exception as err:
        logger.error(traceback.format_exc())
        return abort(500)

@payment.route('/checkout-success', methods=['GET'])
def checkout_success():
    # Display the "Success" page
    pass

@payment.route('/checkout-cancel', methods=['GET'])
def checkout_cancel():
    # Display the "Cancel" page
    pass
