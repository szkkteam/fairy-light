#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
# Internal package imports
try:
    from backend.admin.views import AdminDashboardView
    from backend.api import Api
except ImportError as err:
    # TODO: Throw error?
    pass
else:
    # Flask-Restful must be initialized _AFTER_ the SQLAlchemy extension has
    # been initialized, AND after all views, models, and serializers have
    # been imported. This is because the @api decorators create deferred
    # registrations that depend upon said dependencies having all been
    # completed before Api('api').init_app() gets called
    api = Api('api', prefix='/api/v1')
