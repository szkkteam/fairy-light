#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
from os.path import join
from importlib import import_module
import pkg_resources

# Pip package imports
from loguru import logger
try:
    from flask import current_app
except ImportError as e:
    logger.error(e)

# Internal package imports
from .storages import LocalStorage
from .managers import *
from .files import DEFAULTS

CONF_PREFIX = 'MM_'
PREFIX = '{0}_MM_'
MANAGER_PREFIX = 'MM_{0}_'
STORAGE_PREFIX = 'MM_{0}_'

ALLOWED_CONFIGS = ['URL', 'PREFIX', 'ROOT', 'MANAGER', 'STORAGE', ]

MANAGERS = dict((ep.name, ep) for ep in pkg_resources.iter_entry_points('backend.extensions.file_manager.managers'))
STORAGES = dict((ep.name, ep) for ep in pkg_resources.iter_entry_points('backend.extensions.file_manager.storages'))

def _factory(name, manager, storage, *args, **kwargs):
    manager_class = MANAGERS[manager].load()
    storage_class = MANAGERS[storage].load()
    return manager_class(name, storage_class(*args, **kwargs), *args, **kwargs)

def _config_from_dict(app, name, config, global_config):
    # Override global configuration
    config = { **config, **global_config }

    manager = config.pop('manager', MediaManager.default_manager)
    storage = config.pop('storage', MediaManager.default_storage)

    return _factory(name, manager, storage, **config)

class MediaManager(object):

    key = 'mediamanager'
    name = 'media'

    default_storage = 'local'
    default_manager = 'file'
    default_base_path = ''
    default_extensions = DEFAULTS
    default_prefix = '/media'
    default_url = ''

    def __init__(self, app, *args, **kwargs):
        self.app = app
        if app is not None:
            self.init_app(app, *args, **kwargs)


    def init_app(self, app, *args, **kwargs):
        self.instances = None
        app.extensions = getattr(app, 'extensions', {})
        app.extensions[self.key] = self.instances

    def configure(self, app):
        mm = app.config.get('MEDIA_MANAGER', None)
        mm_instances = {}
        # Media Manager configuration is not exists, try to parse app.config to search for named configuration elements
        global_config = {}
        if mm is None:
            mm = {}
            # Search for individual dict config for different managers
            for key, value in app.config.items():
                if key.startswith(CONF_PREFIX):
                    if key.endswitch(tuple(ALLOWED_CONFIGS)):
                        try:
                            """ Example:
                                MM_PHOTO_MEDIA_URL = # configuration
                            """
                            name, conf_element = key.replace(CONF_PREFIX, '').rsplit('_', 1)
                            name = name.lower()
                            conf_element = conf_element.lower()
                            if name in mm:
                                mm[name][conf_element] = value
                            else:
                                mm[name] = {}
                        except ValueError:
                            """ Example:
                                MM_URL = # configuration
                            """
                            conf_element = key.replace(CONF_PREFIX, '').rsplit('_', 1)
                            conf_element = conf_element.lower()
                            global_config[conf_element] = value

        for key, value in app.config.items():
            if key.startswith(CONF_PREFIX):
                if isinstance(value, dict):
                    """ Example:
                        MM_PHOTO_MEDIA = {
                            # configuration
                        }
                    """
                    name = key.replace(CONF_PREFIX, '').lower()
                    mm_instances[name] = _config_from_dict(app, name, value, global_config)

        # Media manager configuration(s) can be encapsulated in a dictionary
        if isinstance(mm, dict) and len(mm.keys() > 0):
            # If Media Manager instance(s) defined as key = name, value = config_dict
            """ Example:
                MEDIA_MANAGER = {
                    'PHOTO': {
                        # configuration
                    },
                    'FILES':{
                        # configuration
                    }
                }
            """
            if isinstance(mm.keys()[0], dict):
                for name, config in mm.items():
                    mm_instances[name] = _config_from_dict(app, name, config, global_config)
            # Only 1 instance of configuration exists
            else:
                """ Example:
                    MEDIA_MANAGER = {
                        # configuration
                    }
                """
                mm_instances[self.name] = _config_from_dict(app, self.name, mm, global_config)










