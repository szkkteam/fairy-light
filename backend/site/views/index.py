#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import render_template, session, redirect, url_for
from flask_babelex import refresh

# Internal package imports
from backend.shop.inventory import ProductInventory
from backend.site.views.blueprint import site, site_lang

def carousel_test():
    title = 'Album %s'
    text = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit'
    img_link = 'http://placehold.it/285x200'

    return [  ( [ img_link for _ in range(4) ],  title % i, text ) for i in range(6) ]



@site.route('/')
@site.route('/index')
@site_lang.route('/index')
def index():
    return render_template('website/index/index.html',
                           # Shopping Cart
                           cart_num_of_items=ProductInventory.get_num_of_items(),

                           carousel_slides=carousel_test())


@site.route('/lang/<lang_code>')
def set_language(lang_code=None):
    session['language'] = lang_code
    # Refresh the babel cache
    refresh()
    return redirect(url_for('site.index'))