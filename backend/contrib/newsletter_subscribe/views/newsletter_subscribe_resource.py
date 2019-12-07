#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import after_this_request, current_app

# Internal package imports
from backend.api import ModelResource, CREATE, PATCH
from backend.extensions.api import api

from .blueprint import newsletter_subscribe
from ..models import NewsletterSubscribe

@api.model_resource(newsletter_subscribe, NewsletterSubscribe, '/subscribe', '/subscribe/<int:id>')
class NewsletterSubscribeResource(ModelResource):
    include_methods = [CREATE, PATCH]

    # TODO: Create patch and get methods, where check for logged in users.
    # or don't let the user to be able to post the isActive parameter, and dont let users to use patch for changing it. Only through the subsribe and unsubsrcibe views.

    def create(self, newsletter_subscribe, errors):
        print("Create called: ", newsletter_subscribe)
        if errors:
            return self.errors(errors)

        return self.created(newsletter_subscribe)