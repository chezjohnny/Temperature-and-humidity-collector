#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Johnny Mariethoz <Johnny.Mariethoz@rero.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2012 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"


#---------------------------- Modules -----------------------------------------

# import of standard modules
import sys
import os
from optparse import OptionParser

# third party modules
from rdc import create_app
from rdc import default_config

# local modules


#---------------------------- Main Part ---------------------------------------

if __name__ == '__main__':

    usage = "usage: %prog [options]"

    parser = OptionParser(usage)

    parser.set_description ("Run Wsgi application")



    parser.add_option ("-v", "--verbose", dest="verbose",
                       help="Verbose mode",
                       action="store_true", default=False)


    (options,args) = parser.parse_args ()

    if len(args) != 0:
        parser.error("Error: incorrect number of arguments, try --help")
    app = create_app()
    app.secret_key = app.config.get('SECRET_KEY')
    app.run(debug=True)

