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
    scripts=['scripts/rdcclient.py', 'scripts/setcard.py'],
    install_requires=[
        "EasyProcess>=0.1.4",
        "config>=0.3.7",
        "python-daemon>=1.6",
        "lockfile>=0.9.1",
        "pyserial>=2.6",
        "uptime>=3.0.1"
    ]
)
