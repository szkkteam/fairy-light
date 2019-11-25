#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import click
import subprocess

# Pip package imports
# Internal package imports

@click.group()
def celery():
    """Start the celery worker and/or beat."""
    pass


@celery.command()
def worker():
    """Start the celery worker."""
    subprocess.run('celery worker -A wsgi.celery -l debug', shell=True)


@celery.command()
def beat():
    """Start the celery beat."""
    subprocess.run('celery beat -A wsgi.celery -l debug', shell=True)
