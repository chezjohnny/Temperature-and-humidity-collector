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
import urllib2
import json
import datetime
import daemon
import lockfile
import time

import ow
ow.init('u')

# third party modules


# local modules

def temperature():
    root = ow.Sensor( '/' )
    for sensor in root.find( type = 'DS18S20' ):
        return float(sensor.temperature)

def http_post(host, data):
    data_json = json.dumps(data)
    req = urllib2.Request(host, data_json, {'content-type': 'application/json'})
    response_stream = urllib2.urlopen(req)
    response = response_stream.read()
    return response

def post_temperature():
    temp =  temperature()
    now = datetime.datetime.now().isoformat()
    host_name = 'ChezJohnny'
    
    data = { 
        'id' : now + host_name,
        'method' : 'add',
        'params' : {
            'date_statement': now,
            'sensor_value': temp,
            'sensor_type': 'TEMPERATURE',
            'host_name': host_name
        }
    }
    host = 'http://chezjohnny.no-ip.org/rdc'
    http_post(host, data)
#---------------------------- Main Part ---------------------------------------

if __name__ == '__main__':

    usage = "usage: %prog [options]"

    parser = OptionParser(usage)

    parser.set_description ("Change It")



    parser.add_option ("-v", "--verbose", dest="verbose",
                       help="Verbose mode",
                       action="store_true", default=False)
    parser.add_option ("-d", "--daemon", dest="daemon",
                               help="daemon mode",
                               action="store_true",
                               default=False)

    (options,args) = parser.parse_args ()

    if len(args) != 0:
        parser.error("Error: incorrect number of arguments, try --help")
    log_dir = '/var/run/rdc'
    try:
        os.mkdir(log_dir,)
    except OSError:
        pass
    if options.daemon:
        with daemon.DaemonContext(working_directory='/',
                pidfile=lockfile.FileLock(os.path.join(log_dir,'temperature.pid')),
                stdout=file(os.path.join(log_dir,'temperature.log'),'w'),
                stderr=file(os.path.join(log_dir,'temperature.err'), 'w')):
            while True:
                try:
                    post_temperature()
                except Exception, e:
                    sys.stderr.write(str(e))
                time.sleep(60)

    else:
        post_temperature()
