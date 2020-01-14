"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask import render_template, request, url_for, redirect, abort

from flask_breadcrumbs import register_breadcrumb, current_breadcrumbs

from loguru import logger
# Internal package imports


from .blueprint import photo_album

from ..models import Category
from ..models import Event
from ..models import Album
from ..models import Image

def get_prepare_models(get_model, get_img=None, get_url=None):
    all_models = get_model()

    for model in all_models:
        if model.price:
            # category.price = [category.price, category.price * 0.85]
            pass

        model.price = 18
        model.img = get_img(model) if get_img else 'http://placehold.it/285x200'
        model.endpoint = get_url(model) if get_url else '#'

    return all_models


def view_category(*args, **kwargs):
    category_id = request.view_args.get('category')
    model = Category.get(category_id)
    return [{'text': model.title if model else 'Unknown', 'url': url_for('photo_album.events', category=category_id)}]

def view_event(*args, **kwargs):
    category_id = request.view_args.get('category')
    event_id = request.view_args.get('event')
    model = Event.get(event_id)
    return [{'text': model.title if model else 'Unknown', 'url': url_for('photo_album.albums', category=category_id, event=event_id)}]

def view_album(*args, **kwargs):
    category_id = request.view_args.get('category')
    event_id = request.view_args.get('event')
    album_id = request.view_args.get('album')
    model = Album.get(album_id)
    return [{'text': model.title if model else 'Unknown', 'url': url_for('photo_album.photos', category=category_id, event=event_id, album=album_id)}]


@photo_album.route('/')
@photo_album.route('/categories')
@register_breadcrumb(photo_album, '.', 'Home' )
def categories():
    try:
        photos_model = get_prepare_models(lambda : Category.get_all_by(is_public=True),
                                          get_url=lambda model: url_for('photo_album.events', category=model.id))

        return render_template('photos_listing.html', photos=photos_model)
    except Exception as e:
        logger.error(e)
        return abort(404)


@photo_album.route('/categories/<int:category>/events')
@register_breadcrumb(photo_album, '.category', '', dynamic_list_constructor=view_category)
def events(category):
    try:
        is_public = Category.get(category).is_public
        if not is_public:
            return abort(403)

        photos_model = get_prepare_models(lambda : Event.get_all_by(is_public=True, category_id=category),
                                          get_url=lambda model: url_for('photo_album.albums', category=category, event=model.id))

        return render_template('photos_listing.html', photos=photos_model)
    except Exception as e:
        logger.error(e)
        return abort(404)


@photo_album.route('/categories/<int:category>/events/<int:event>/albums')
@register_breadcrumb(photo_album, '.category.event', '', dynamic_list_constructor=view_event)
def albums(category, event):
    try:
        is_public = Event.get(event).is_public
        if not is_public:
            return abort(403)

        photos_model = get_prepare_models(lambda : Album.get_all_by(is_public=True, event_id=event),
                                          get_url=lambda model: url_for('photo_album.photos',category=category, event=event, album=model.id))

        if len(photos_model) == 1:
            return redirect(url_for('photo_album.photos', category=category, event=event, album=photos_model[0].id))

        return render_template('photos_listing.html', photos=photos_model)
    except Exception as e:
        logger.error(e)
        return abort(404)


@photo_album.route('/categories/<int:category>/events/<int:event>/albums/<int:album>/photos')
@register_breadcrumb(photo_album, '.category.event.album', '', dynamic_list_constructor=view_album)
def photos(category, event, album):
    try:
        is_public = Album.get(album).is_public
        if not is_public:
            return abort(403)

        photos_model = get_prepare_models(lambda: Image.get_all_by(album_id=album),
                                          get_img=lambda model: model.get_thumbnail_path(),
                                          get_url=lambda model: model.get_image_path())

        return render_template('photos_images_listing.html', photos=photos_model)
    except Exception as e:
        logger.error(e)
        return abort(404)
"""