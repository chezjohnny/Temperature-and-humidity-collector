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
import random
import datetime
from sqlalchemy import and_

# third party modules


# local modules


def generate(n):
    now = datetime.datetime.now()
    delta = datetime.timedelta(minutes=5)
    start = now-delta*n
    return [(now-delta*(n-v) , (random.random()*10)-5) for v in range(n)]

def create(name, state, types=['TEMPERATURE', 'BALANCE', 'EXPIRATION'],
        n=8640):
    data = generate(n)
    dc = DataCollector(name, state, "0", "-3","+41788129088")
    for d in data:
        sensor_type = random.choice(types)
        value = str(d[1])
        if sensor_type == 'EXPIRATION':
            value = d[0].isoformat()
        s = DataSensors(d[0], value, sensor_type)
        dc.data.append(s)
        dc.last_sensor_value = value
        dc.last_sensor_type = sensor_type
    rdc.db.session.add(dc)
    rdc.db.session.commit()
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

    os.environ['RDC_SETTINGS'] = '/usr/local/rdc/rdc_server.cfg'
    import rdc
    app = rdc.create_app()
    app.test_request_context().push()

    import datetime
    from rdc.models import DataSensors
    from rdc.models import DataCollector
    rdc.db.drop_all()
    rdc.db.create_all()
    #create('localhost','DISABLE')
    #create('ChezJohnny','ENABLE')
    #create('ChezArnold','WARNING')
    #create('ChezUnAutre','CRITICAL')
    create('Test','DISABLE')
    #for dc in DataCollector.query.all():
    #    print "Temp: %s %s" % dc.last_value()
    #    print "Bal: %s %s" % dc.last_value('BALANCE')
    #    print "Exp: %s %s" % dc.last_value('EXPIRATION')

    #now = datetime.datetime.now()
    #for dc in DataCollector.query.all():
    #    #print dc
    #    from_date = now - datetime.timedelta(days=1)
    #    to_date = now
    #    print dc.get_data(from_date, to_date,'TEMPERATURE', 10)
    #    #print DataSensors.query.filter(and_(DataSensors.collector_id==dc.id,
    #    #    DataSensors.sensor_type=='TEMPERATURE')).filter(and_(DataSensors.date_statement
    #    #        <= to_date, DataSensors.date_statement >= from_date,
    #    #        DataSensors.sensor_value !=
    #    #        'NULL')).order_by(DataSensors.date_statement).all()
