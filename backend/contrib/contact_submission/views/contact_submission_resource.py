#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import after_this_request, current_app

# Internal package imports
from backend.api import ModelResource, CREATE
from backend.extensions.api import api
from backend.utils import send_mail

from .blueprint import csub
from ..models import ContactSubmission

@api.model_resource(csub, ContactSubmission, '/contact-submissions')
class UserResource(ModelResource):
    include_methods = [CREATE]

    def create(self, contact_submission, errors):
        if errors:
            return self.errors(errors)

        send_mail(subject='New Contact Submission',
                  recipients=list(current_app.config.get('MAIL_ADMINS')),
                  template='email/contact_submission.html',
                  contact_submission=contact_submission)

        return self.created(contact_submission)