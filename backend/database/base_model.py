#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
# Pip package imports
from sqlalchemy.ext.declarative import declared_attr

from sqlalchemy.orm import remote, foreign
#from sqlalchemy.event import listens_for
from sqlalchemy import func
from sqlalchemy import Index, Sequence
from sqlalchemy.sql import expression
from sqlalchemy_utils import LtreeType, Ltree
from sqlalchemy_utils.types.ltree import LQUERY

# Internal package imports
from backend.extensions import db
from backend.utils import pluralize, title_case


class BaseModel(db.Model):
    """Base table class. It includes convenience methods for creating,
    querying, saving, updating and deleting models.
    """
    __abstract__ = True
    __table_args__ = {'extend_existing': True}

    __repr_props__ = ()
    """Set to customize automatic string representation.

    For example::

        class User(database.Model):
            __repr_props__ = ('id', 'email')

            email = Column(String)

        user = User(id=1, email='foo@bar.com')
        print(user)  # prints <User id=1 email="foo@bar.com">
    """

    @declared_attr
    def __plural__(self):
        return pluralize(self.__name__)

    @declared_attr
    def __label__(self):
        return title_case(self.__name__)

    @declared_attr
    def __plural_label__(self):
        return pluralize(self.__label__)

    @classmethod
    def all(cls):
        """Get all models."""
        return cls.query.all()

    @classmethod
    def get(cls, id):
        """Get one model by ID.

        :param id: The model ID to get.
        """
        return cls.query.get(int(id))

    @classmethod
    def get_by(cls, **kwargs):
        """Get one model by keyword arguments.

        :param kwargs: The model attribute values to filter by.
        """
        return cls.query.filter_by(**kwargs).first()

    @classmethod
    def get_all_by(cls, **kwargs):
        """Get all model by keyword arguments.

        :param kwargs: The model attribute values to filter by.
        """
        return cls.query.filter_by(**kwargs).all()

    @classmethod
    def get_or_create(cls, commit=False, **kwargs):
        """Get or create model by keyword arguments.

        :param bool commit: Whether or not to immediately commit the DB session (if create).
        :param kwargs: The model attributes to get or create by.
        """
        instance = cls.get_by(**kwargs)
        if not instance:
            instance = cls.create(**kwargs, commit=commit)
        return instance

    @classmethod
    def join(cls, *props, **kwargs):
        return cls.query.join(*props, **kwargs)

    @classmethod
    def filter(cls, *args, **kwargs):
        return cls.query.filter(*args, **kwargs)

    #@classmethod
    #def filter_in(cls, *args, **kwargs):

    @classmethod
    def filter_by(cls, **kwargs):
        """Find models by keyword arguments.

        :param kwargs: The model attribute values to filter by.
        """
        return cls.query.filter_by(**kwargs)

    @classmethod
    def create(cls, commit=False, **kwargs):
        """Create a new model and add it to the database session.

        :param bool commit: Whether or not to immediately commit the DB session.
        :param kwargs: The model attribute values to create the model with.
        """
        instance = cls(**kwargs)
        return instance.save(commit)

    def update(self, commit=False, **kwargs):
        """Update fields on the model.

        :param bool commit: Whether or not to immediately commit the DB session.
        :param kwargs: The model attribute values to update the model with.
        """
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return self.save(commit)

    def save(self, commit=False):
        """Save the model.

        :param bool commit: Whether or not to immediately commit the DB session.
        """
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=False):
        """Delete the model.

        :param bool commit: Whether or not to immediately commit the DB session.
        """
        db.session.delete(self)
        return commit and db.session.commit()

    def __repr__(self):
        properties = [f'{prop}={getattr(self, prop)!r}'
                      for prop in self.__repr_props__ if hasattr(self, prop)]
        return f"<{self.__class__.__name__} {' '.join(properties)}>"

id_seq = Sequence('nodes_id_seq')

class TreeBaseModel(db.Model):
    """Base table class. It includes convenience methods for creating,
    querying, saving, updating and deleting models.
    """
    id = Column(BigInteger, id_seq, primary_key=True)
    # LTree path
    path = Column(LtreeType, nullable=False)
    parent = relationship(
        'TreeBaseModel',
        primaryjoin=remote(path) == foreign(func.subpath(path, 0, -1)),
        backref='children',
        viewonly=True, )

    __abstract__ = True

    __table_args__ = (
                        Index('ix_nodes_path', path, postgresql_using="gist"),
                        {'extend_existing': True}
                      )

    __repr_props__ = ()
    """Set to customize automatic string representation.

    For example::

        class User(database.Model):
            __repr_props__ = ('id', 'email')

            email = Column(String)

        user = User(id=1, email='foo@bar.com')
        print(user)  # prints <User id=1 email="foo@bar.com">
    """

    def __init__(self, name, parent=None):
        _id = db.engine.execute(id_seq)
        self.id = _id
        self.name = name
        ltree_id = Ltree(str(_id))
        self.path = ltree_id if parent is None else parent.path + ltree_id

    @declared_attr
    def __plural__(self):
        return pluralize(self.__name__)

    @declared_attr
    def __label__(self):
        return title_case(self.__name__)

    @declared_attr
    def __plural_label__(self):
        return pluralize(self.__label__)

    @property
    def depth(self):
        return len(self.path.split('.')) - 1

    @classmethod
    def all(cls):
        """Get all models."""
        return cls.query.all()

    @classmethod
    def get(cls, id):
        """Get one model by ID.

        :param id: The model ID to get.
        """
        return cls.query.get(int(id))

    @classmethod
    def get_by(cls, **kwargs):
        """Get one model by keyword arguments.

        :param kwargs: The model attribute values to filter by.
        """
        return cls.query.filter_by(**kwargs).first()

    @classmethod
    def get_all_by(cls, **kwargs):
        """Get all model by keyword arguments.

        :param kwargs: The model attribute values to filter by.
        """
        return cls.query.filter_by(**kwargs).all()

    @classmethod
    def get_root(cls):
        return db.session.query(TreeBaseModel).filter(func.nlevel(TreeBaseModel.path) == 1)

    @classmethod
    def get_siblings(cls, id, include=True):
        sibling = cls.get_by(id)
        siblings_same_lvl = db.session.query(TreeBaseModel).filter(
            TreeBaseModel.path.descendant_of(sibling.path[:-1]),
            func.nlevel(TreeBaseModel.path) == len(sibling.path))
        if include:
            return siblings_same_lvl
        return siblings_same_lvl.filter(
            TreeBaseModel.id != sibling.id)

    @classmethod
    def get_immediate_childrens(cls, id):
        if id is None:
            # If ID is None get the childrens of the root node, so all first level Nodes
            query = "*{1}"
        else:
            query = "*.%s{1}" % id
        lquery = expression.cast(query, LQUERY)
        return db.session.query(TreeBaseModel).filter(TreeBaseModel.path.lquery(lquery))

    @classmethod
    def get_all_parents(cls, id):
        beginning_getter = Session.query(TreeBaseModel). \
            filter(TreeBaseModel.id == id).cte(name='parent_for', recursive=True)
        with_recursive = beginning_getter.union_all(
            db.session.query(TreeBaseModel).filter(TreeBaseModel.id == beginning_getter.c.parent_id)
        )
        return db.session.query(with_recursive).order_by(cls.path.desc())

    @classmethod
    def get_or_create(cls, commit=False, **kwargs):
        """Get or create model by keyword arguments.

        :param bool commit: Whether or not to immediately commit the DB session (if create).
        :param kwargs: The model attributes to get or create by.
        """
        instance = cls.get_by(**kwargs)
        if not instance:
            instance = cls.create(**kwargs, commit=commit)
        return instance

    @classmethod
    def join(cls, *props, **kwargs):
        return cls.query.join(*props, **kwargs)

    @classmethod
    def filter(cls, *args, **kwargs):
        return cls.query.filter(*args, **kwargs)

    #@classmethod
    #def filter_in(cls, *args, **kwargs):

    @classmethod
    def filter_by(cls, **kwargs):
        """Find models by keyword arguments.

        :param kwargs: The model attribute values to filter by.
        """
        return cls.query.filter_by(**kwargs)

    @classmethod
    def create(cls, commit=False, **kwargs):
        """Create a new model and add it to the database session.

        :param bool commit: Whether or not to immediately commit the DB session.
        :param kwargs: The model attribute values to create the model with.
        """
        instance = cls(**kwargs)
        return instance.save(commit)

    def update(self, commit=False, **kwargs):
        """Update fields on the model.

        :param bool commit: Whether or not to immediately commit the DB session.
        :param kwargs: The model attribute values to update the model with.
        """
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return self.save(commit)

    def save(self, commit=False):
        """Save the model.

        :param bool commit: Whether or not to immediately commit the DB session.
        """
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=False):
        """Delete the model.

        :param bool commit: Whether or not to immediately commit the DB session.
        """
        db.session.delete(self)
        return commit and db.session.commit()

    def __repr__(self):
        properties = [f'{prop}={getattr(self, prop)!r}'
                      for prop in self.__repr_props__ if hasattr(self, prop)]
        return f"<{self.__class__.__name__} {' '.join(properties)}>"

