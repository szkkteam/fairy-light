#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import render_template

# Internal package imports
from backend.shop.inventory import ProductInventory
from backend.site.views.blueprint import site

def carousel_test():
    title = 'Album %s'
    text = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit'
    img_link = 'http://placehold.it/285x200'

    return [  ( [ img_link for _ in range(4) ],  title % i, text ) for i in range(6) ]



@site.route('/')
@site.route('/index')
def index():
    return render_template('website/index/index.html',
                           # Shopping Cart
                           cart_num_of_items=ProductInventory.get_num_of_items(),

                           carousel_slides=carousel_test())


