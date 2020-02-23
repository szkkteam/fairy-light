#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import inspect

# Pip package imports
import click
from flask import current_app

# Internal package imports



@click.argument('url')
@click.option('--method', default='GET',
              help='Method for url to match (default: GET)')
def url(url, method):
    pass


@click.option('--order', default='rule',
              help='Property on Rule to order by (default: rule)')
def urls(order):
    pass