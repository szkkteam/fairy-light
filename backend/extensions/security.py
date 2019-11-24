#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
# Internal package imports
try:
    from backend.extensions import db
    from backend.security import SQLAlchemyUserDatastore, Security
    from backend.security.models import User, Role
except ImportError as err:
    # TODO: Log error?
    pass
else:
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(datastore=user_datastore)
