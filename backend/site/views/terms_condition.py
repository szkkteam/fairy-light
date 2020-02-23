#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import render_template

# Internal package imports
from backend.shop.inventory import ProductInventory
from backend.site.views.blueprint import site

@site.route('/terms-and-conditions')
def tc_shop():
    return render_template('website/tc/shop.html',
                           )
@site.route('/privacy-policy')
def privacy_policy():
    return render_template('website/tc/privacy.html')

@site.route('/cookies-policy')
def cookie_policy():
    return render_template('website/tc/cookie.html')

@site.route('/return-refund')
def refund_policy():
    return render_template('website/tc/refund.html')

@site.route('/terms-of-service')
def service_policy():
    return render_template('website/tc/service.html')

@site.route('/disclaimer')
def disclaimer():
    return render_template('website/tc/disclaimer.html')
