#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import render_template

# Internal package imports
from backend.shop.inventory import ProductInventory
from backend.site.views.blueprint import site, site_lang

from ..social import get_twitter_meta, get_facebook_meta

@site.route('/services')
@site_lang.route('/services')
def services():
    return render_template('website/services/services.html',
                           # Shopping Cart
                           cart_num_of_items=ProductInventory.get_num_of_items(),

                           # Social
                           facebook=get_facebook_meta(),
                           twitter=get_twitter_meta(),
                           )


