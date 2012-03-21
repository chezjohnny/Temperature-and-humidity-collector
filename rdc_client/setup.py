#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Client for remote date collector."""
__author__ = "Johnny Mariethoz <chezjohnny@gmail.com>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2012 Rero, Johnny Mariethoz"
__license__ = "GPL"


from setuptools import setup, find_packages

setup(
    name='RDCClient',
    version='1.0',
    long_description=__doc__,
    packages=['rdcc'],
    zip_safe=False,
    scripts=['scripts/rdcclient.py'],
    install_requires=[
    #'Flask>=0.2',
    #'SQLAlchemy>=0.6',
    #'Flask-Login>=0.1',
    #'Flask-WTF>=0.5',
    #'Flask-Babel>=0.8'
    'pyserial>=2.6'
    ]
)
