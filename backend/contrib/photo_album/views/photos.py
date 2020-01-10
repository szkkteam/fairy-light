#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import render_template

# Internal package imports
from .blueprint import photo_album

@photo_album.route('/')
def index():
    return render_template('photos.html')

@photo_album.route('/categories')
def categories():
    """ Listing all the available categories with cover photo and num of images. """
    pass

@photo_album.route('/categories/<int:category>')
def events(category):
    """ Listing all the available events for that specific category with cover photo and num of images. """
    pass

@photo_album.route('/events/<int:event>')
def albums(event):
    """ Listing all available albums for that specific event with cover photo and num of images.
        If only 1 album exists redirect to that album immidiatly.
    """
    pass

@photo_album.route('/albums/<int:album>')
def a_photos(album):
    """ Listing all the available photos in that individual """
    pass