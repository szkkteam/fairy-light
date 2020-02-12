#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import random
import string
import traceback
import sys
import enum

# Pip package imports
from flask import current_app, render_template, url_for, request, redirect, jsonify, abort, session
from flask.views import MethodView

from loguru import logger

import stripe

# Internal package imports
from backend.extensions import csrf

class StripeEvents(enum.Enum):

    # Payment intent events
    payment_intent_created = "payment_intent.created"
    payment_intent_failed = "payment_intent.failed"
    payment_intent_succeeded = "payment_intent.succeeded"

    # Charge events
    charge_succeeded = "charge.succeeded"
    charge_failed = "charge.failed"


class StripeWebhook(MethodView):
    #methods = ['POST']
    decorators = [csrf.exempt]

    def return_success(self):
        return jsonify({'status': 'success'})

    def return_error(self, msg, code=403):
        return jsonify({'error': msg}), code

    # Payment Intent handlers
    def handle_payment_intent_created(self, data):
        return self.return_success()

    def handle_payment_intent_succeeded(self, data):
        return self.return_success()

    def handle_payment_intent_failed(self, data):
        return self.return_success()

    # Charge handlers
    def handle_charge_succeeded(self, data):
        return self.return_success()

    def handle_charge_failed(self, data):
        return self.return_success()

    # Event Handlers
    def handle_payment_intent(self, event, data):
        logger.debug('Webhook event: \'%s\' called.' % event)
        if event == StripeEvents.payment_intent_created:
            return self.handle_payment_intent_created(data)
        elif event == StripeEvents.payment_intent_succeeded:
            return self.handle_payment_intent_succeeded(data)
        elif event == StripeEvents.payment_intent_failed:
            return self.handle_payment_intent_failed(data)
        else:
            logger.error('Sub event: \'%s\' not handled.' % event)
            return self.return_success()

    def handle_charge(self, event, data):
        logger.debug('Webhook event: \'%s\' called.' % event)
        if event == StripeEvents.charge_succeeded:
            return self.handle_charge_succeeded(data)
        if event == StripeEvents.charge_failed:
            return self.handle_charge_failed(data)
        else:
            logger.error('Sub event: \'%s\' not handled.' % event)
            return self.return_success()

    def post(self):
        try:
            request_data = request.get_json()
            # Get the secret key
            webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
            if webhook_secret:
                # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
                signature = request.headers.get('stripe-signature')
                print("signature: ", signature, flush=True)
                print("Request data: ", request.data, flush=True)
                try:
                    event = stripe.Webhook.construct_event(
                        payload=request.data, sig_header=signature, secret=webhook_secret)
                    data = event['data']
                    # Get the type of webhook event sent - used to check the status of PaymentIntents.
                    event_type = event['type']
                except stripe.error.SignatureVerificationError as e:
                    logger.error(e)
                    return self.return_error('Webhook signature header is invalid', 400)
                except Exception as e:
                    logger.error(traceback.format_exc())
                    return self.return_error('Unknown error', 500)
            else:
                data = request_data['data']
                event_type = request_data['type']
            data_object = data['object']

            if data_object['object'] == 'payment_intent':
                ev = StripeEvents(event_type)
                return self.handle_payment_intent(ev, data_object)

            if data_object['object'] == 'charge':
                ev = StripeEvents(event_type)
                return self.handle_charge(ev, data_object)

            else:
                #print("data_object: ", data_object, flush=True)
                logger.error('event \'%s\' not handled' % event_type)
                self.return_success()

        except Exception as err:
            logger.error(traceback.format_exc())
            self.return_error('Unknown error occured during request', 500)

