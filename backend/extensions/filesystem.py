#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
import flask_fs

# Internal package imports

class FileSystem(object):

    def init_app(self, app):
        self.state = flask_fs.init_app(app)

fs = FileSystem()