#!/usr/bin/env python

# -*- coding: utf-8 -*-

__author__ = "Johnny Mariethoz <Johnny.Mariethoz@rero.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2009 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"


#---------------------------- Modules -----------------------------------------

# import of standard modules
import sys
import os
from optparse import OptionParser

# third party modules


# local modules


#---------------------------- Main Part ---------------------------------------

if __name__ == '__main__':

    usage = "usage: %prog [options]"

    parser = OptionParser(usage)

    parser.set_description ("Change It")



    parser.add_option ("-v", "--verbose", dest="verbose",
                       help="Verbose mode",
                       action="store_true", default=False)


    (options,args) = parser.parse_args ()

    if len(args) != 0:
        parser.error("Error: incorrect number of arguments, try --help")


    import datetime
    from rdc.models import DataSensors
    import rdc
    rdc.db.drop_all()
    rdc.db.create_all()
    now = datetime.datetime.now()
    s = DataSensors(now, "2.3", "TEMPERATURE")
    from rdc.models import DataCollector
    d = DataCollector('localhost', 'ENABLED',now, "2.3", "TEMPERATURE", "0",
"-3","+41788129088")
    d.data.append(s)
    rdc.db.session.add(d)
    rdc.db.session.commit()
    for data in DataCollector.query.all():
        print data
        for d in data.data:
            print d
