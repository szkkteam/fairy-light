#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
# Internal package imports
import stripe as stripe_base

class Stripe(object):

    def init_app(self, app):
        stripe_base.api_key = app.config['STRIPE_SECRET_KEY']

stripe = Stripe()