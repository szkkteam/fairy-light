#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os
import pytest

# Pip package imports
from backend.extensions.mail import mail

# Internal package imports
from backend.app import _create_app
from backend.config import TestConfig

@pytest.fixture(autouse=True, scope='session')
def app():
    app = _create_app(TestConfig)
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()

@pytest.fixture()
def outbox():
    with mail.record_messages() as messages:
        yield messages
