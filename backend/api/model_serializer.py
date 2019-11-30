#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from flask_sqlalchemy.model import camel_to_snake_case
from marshmallow.exceptions import ValidationError

# Internal package imports
from backend.extensions.marshmallow import ma

from .constants import READ_ONLY_FIELDS
from .utils import to_camel_case


class ModelSerializer(ma.ModelSchema):
    """
    Base class for database model serializers. This is pretty much a stock
    :class:`flask_marshmallow.sqla.ModelSchema`: it will automatically create
    fields from the attached database Model, the only difference being that it
    will automatically dump to (and load from) the camel-cased variants of the
    field names.

    For example::

        from backend.api import ModelSerializer
        from backend.security.models import Role

        class RoleSerializer(ModelSerializer):
            class Meta:
                model = Role

    Is roughly equivalent to::

        from marshmallow import Schema, fields

        class RoleSerializer(Schema):
            id = fields.Integer()
            name = fields.String()
            description = fields.String()
            created_at = fields.DateTime(dump_to='createdAt',
                                         load_from='createdAt')
            updated_at = fields.DateTime(dump_to='updatedAt',
                                         load_from='updatedAt')

    Obviously you probably shouldn't be loading `created_at` or `updated_at`
    from JSON; it's just an example to show the automatic snake-to-camelcase
    field naming conversion.
    """

    def is_create(self):
        """Check if we're creating a new object. Note that this context flag
        must be set from the outside, ie when the class gets instantiated.
        """
        return self.context.get('is_create', False)

    """
    def handle_error(self, error, data, *args, **kwargs):
        Customize the error messages for required/not-null validators with
        dynamically generated field names. This is definitely a little hacky
        (it mutates state, uses hardcoded strings), but unsure how better to do it

        required_messages = ('Missing data for required field.',
                             'Field may not be null.')
        for field_name in error.field_names:
            for i, msg in enumerate(error.messages[field_name]):
                if msg in required_messages:
                    label = camel_to_snake_case(field_name).replace('_', ' ').title()
                    error.messages[field_name][i] = f'{label} is required.'
        """

    def on_bind_field(self, field_name, field_obj):
        def camelcase(s):
            parts = iter(s.split("_"))
            return next(parts) + "".join(i.title() for i in parts)


        converted = camelcase(field_obj.data_key or field_name)
        field_obj.data_key = converted


    def validate_id(self, id):
        if self.is_create() or int(id) == int(self.instance.id):
            return
        raise ValidationError('ids do not match')
