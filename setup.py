#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Common Python library imports
import os
from codecs import open

# Pip package imports
from setuptools import setup, find_packages

# Internal package imports
import backend

# Get the project root directory
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

# Open the readme file
with open(os.path.join(ROOT_DIR, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


def is_pkg(line):
    return line and not line.startswith(('--', 'git', '#'))

def read_requirements(filename):
    with open(os.path.join(ROOT_DIR, filename), encoding='utf-8') as f:
        return [line for line in f.read().splitlines() if is_pkg(line)]

install_requires = read_requirements('requirements.txt')
dev_requires = read_requirements('requirements-dev.txt')

setup(
    name='fairy_light',
    version=backend.__version__,
    description=backend.__doc__,
    long_description=long_description,
    url=backend.__homepage__,
    author=backend.__author__,
    license=backend.__license__,

    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: System :: Software Distribution',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
    ],
    packages=find_packages(exclude=['ansible', 'tests']),
    install_requires=install_requires,
    extras_require={'test': dev_requires, 'docs': dev_requires},
    include_package_data=True,
    zip_safe=False,
    entry_points='''
        [console_scripts]
        flask=manage:main
    ''',
)
