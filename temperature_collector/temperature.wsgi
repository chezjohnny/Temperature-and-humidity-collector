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

from webob import Request, Response
from webob import exc
from simplejson import loads, dumps
import traceback
import sys
import datetime
import re

from sqlalchemy.types import String, DateTime, Integer
from sqlalchemy import Table, MetaData, Column, create_engine, and_
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import sessionmaker
Session = sessionmaker()
engine = create_engine('mysql://abricot:pwd4abri@localhost/abricotsdb')
Session.configure(bind=engine)

Base = declarative_base()


class DataSensors(Base):
    __tablename__ = 'collected_data'
    id = Column(Integer, primary_key=True)
    date_statement =  Column(DateTime())
    sensor_value =  Column(String(50))
    sensor_type =  Column(String(50))
    host_name =  Column(String(50))
    def __init__(self, date_statement, sensor_value, sensor_type, host_name):
        self.date_statement = date_statement
        self.sensor_value = sensor_value
        self.sensor_type = sensor_type
        self.host_name = host_name
    def __repr__(self):
        return "<DataSensors('%s','%s', '%s', '%s')>" % (self.date_statement, self.sensor_value, self.sensor_type, self.host_name)

def create_all():
    Base.metadata.create_all(engine)
class DataCollector(object):

    def __init__(self):
        self._session = Session()

    def add(self, date_statement, sensor_value, sensor_type, host_name):
        date_satement = datetime.datetime.strptime(date_statement, '%Y-%m-%dT%H:%M:%S.%f')
        data_sensor = DataSensors(date_statement, sensor_value, sensor_type, host_name)
        self._session.add(data_sensor)
        self._session.flush()

    def get_temperatures(self,  host_name, sensor_type='TEMPERATURE',
            from_date=None, to_date=None):
        query = self._session.query(DataSensors)
        values = []
        if to_date is None:
            to_date = datetime.datetime.now()
        if from_date is None:
            from_date = datetime.datetime(2000, 1, 1)
        for data in query.filter_by(sensor_type=sensor_type,
                host_name=host_name).filter(and_(DataSensors.date_statement <=
                        to_date, DataSensors.date_statement >= from_date)).order_by(DataSensors.date_statement).all():
            #values.append([float(data.sensor_value),
            #    float(data.date_statement.strftime('%s'))*1000])
            values.append([
                float(data.date_statement.strftime('%s'))*1000,
                float(data.sensor_value)
                ])
        return values

    
class DispatcherApp(object):
    def __init__(self):
        self._data_collector = DataCollector()
        self._data_collector_rpc = JsonRpcApp(self._data_collector) 
        self._index = IndexApp()

    def __call__(self, environ, start_response):
        req = Request(environ)
        if req.method == 'POST':
            return self._data_collector_rpc(environ, start_response)
        else:
            sys.stderr.write(environ['PATH_INFO']+"\n")
            if re.search(r'/get', environ['PATH_INFO']):
                temps = self._data_collector.get_temperatures(host_name='Chezjohnny')
                resp = Response(
                    status=200,
                    content_type='application/json',
                    body=dumps(temps))
            else:
                return self._index(environ, start_response)

        return resp(environ, start_response)

class IndexApp(object):
    def __call__(self, environ, start_response):
        resp = Response(
                status=200,
                content_type='text/html; charset=utf-8',
                body="""
	<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
	<html>
		<head>
				<title>Temperature</title>
						<meta http-equiv="content-type" content="text/html; charset=utf-8" />
						<meta name="description" content="" />
						<meta name="keywords" content="" />

						<script src="/js/jquery.min.js" type="text/javascript"></script> 
						<script src="/js/jquery.flot.js" type="text/javascript"></script> 
						<link href="/css/main-1.0.css" rel="stylesheet" type="text/css" /> 
						<script>
							$(function () {
                  function onDataReceived(series) {
                      // we get all the data in one go, if we only got partial
                      // data, we could merge it with what we already got
								      //console.log(series.Home);
                      data = [ series ];
                
                      $.plot($("#placeholder"), data, { xaxis: { mode: "time" }});
            }
    
        $.ajax({
            url: '/temperature/get',
            method: 'GET',
            dataType: 'json',
            success: onDataReceived
        });
							});
						</script>
			<style>
#placeholder {
	width: 600px;
	height: 300px;
	margin: 40px auto 0 auto;
}
			</style>
		</head>
		<body>
		<div id="main-page">
		  <h2>Temperature actuelle</h2>
                  <div class="info">
                  </div>
			<h2>Temperature des dernieres 24 heures</h2>
			<div id="placeholder"></div>
		</div>
		</body>
	</html>
                
                """.encode('utf-8'))
        return resp(environ, start_response)

class JsonRpcApp(object):
    """
    Serve the given object via json-rpc (http://json-rpc.org/)
    """

    def __init__(self, obj):
        self.obj = obj

    def __call__(self, environ, start_response):
        req = Request(environ)
        try:
            resp = self.process(req)
        except ValueError, e:
            resp = exc.HTTPBadRequest(str(e))
        except exc.HTTPException, e:
            resp = e
        return resp(environ, start_response)

    def process(self, req):
        if not req.method == 'POST':
            raise exc.HTTPMethodNotAllowed(
                "Only POST allowed",
                allowed='POST')
        try:
            json = loads(req.body)
        except ValueError, e:
            raise ValueError('Bad JSON: %s' % e)
        try:
            method = json['method']
            params = json['params']
            id = json['id']
        except KeyError, e:
            raise ValueError(
                "JSON body missing parameter: %s" % e)
        if method.startswith('_'):
            raise exc.HTTPForbidden(
                "Bad method name %s: must not start with _" % method)
        if not isinstance(params, dict):
            print 'toto'
            raise ValueError(
                "Bad params %r: must be a list" % params)
        try:
            method = getattr(self.obj, method)
        except AttributeError:
            raise ValueError(
                "No such method %s" % method)
        try:
            result = method(**params)
        except:
            text = traceback.format_exc()
            exc_value = sys.exc_info()[1]
            error_value = dict(
                name='JSONRPCError',
                code=100,
                message=str(exc_value),
                error=text)
            return Response(
                status=500,
                content_type='application/json',
                body=dumps(dict(result=None,
                                error=error_value,
                                id=id)))
        return Response(
            content_type='application/json',
            body=dumps(dict(result=result,
                            error=None,
                            id=id)))

application = DispatcherApp()

#---------------------------- Main Part ---------------------------------------

if __name__ == '__main__':

    usage = "usage: %prog [options]"

    parser = OptionParser(usage)

    parser.set_description ("Change It")



    parser.add_option ("-v", "--verbose", dest="verbose",
                       help="Verbose mode",
                       action="store_true", default=False)

    parser.add_option ("-p", "--port", dest="port",
                       help="Http Port (Default: 4041)",
                       type="int", default=4041)


    (options,args) = parser.parse_args ()

    if len(args) != 0:
        parser.error("Error: incorrect number of arguments, try --help")


    from wsgiref.simple_server import make_server
    application = DispatcherApp()
    server = make_server('', options.port, application)
    server.serve_forever()
