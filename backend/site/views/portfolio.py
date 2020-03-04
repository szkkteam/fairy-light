#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import render_template

# Internal package imports
from backend.shop.inventory import ProductInventory
from backend.site.views.blueprint import site, site_lang

from ..social import get_facebook_meta, get_twitter_meta

@site.route('/portfolio')
@site_lang.route('/portfolio')
def portfolio():
    return render_template('website/portfolio/portfolio.html',
                           # Shopping Cart
                           cart_num_of_items=ProductInventory.get_num_of_items(),

                           # Social
                           facebook=get_facebook_meta(),
                           twitter=get_twitter_meta(),
                           )


