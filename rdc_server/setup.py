#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" WebTest to test Flask."""
__author__ = "Johnny Mariethoz <Johnny.Mariethoz@rero.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2012 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"


from setuptools import setup, find_packages

setup(
    name='RDC',
    version='1.0',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    #'Flask>=0.2',
    #'SQLAlchemy>=0.6',
    #'Flask-Login>=0.1',
    #'Flask-WTF>=0.5',
    #'Flask-XML-RPC>=0.1.2',
    #'Flask-SQLAlchemy>=0.15'
    ]
)
