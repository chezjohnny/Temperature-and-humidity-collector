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

from sqlalchemy import desc, asc
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
    
    def get_hosts(self):
        from sqlalchemy import distinct
        results = self._session.query(distinct(DataSensors.host_name))
        return [v[0] for v in results]

    def get_sensor_types(self):
        from sqlalchemy import distinct
        results = self._session.query(distinct(DataSensors.sensor_type))
        return [v[0] for v in results]

    def get_infos(self, host_name):
        query = self._session.query(DataSensors)
        sensor_types = self.get_sensor_types()
        to_return = {}
        for sensor_type in sensor_types:
            to_return[sensor_type] = query.filter_by(sensor_type=sensor_type, host_name=host_name).filter(DataSensors.sensor_value != 'NULL').order_by(desc(DataSensors.date_statement)).first()
        return to_return
                

    def get_month_temperatures(self,  host_name, sensor_type='TEMPERATURE',
            from_date=None, to_date=None):
        query = self._session.query(DataSensors)
        values = []
        if to_date is None:
            to_date = datetime.datetime.now()
        if from_date is None:
            #from_date = datetime.datetime(2000, 1, 1)
            from_date = datetime.datetime.now() - datetime.timedelta(days=31)
        n = 0

        for data in query.filter_by(sensor_type=sensor_type,
                host_name=host_name).filter(and_(DataSensors.date_statement <=
                        to_date, DataSensors.date_statement >= from_date,
                        DataSensors.sensor_value != 'NULL')).order_by(DataSensors.date_statement).all():
            #values.append([float(data.sensor_value),
            #    float(data.date_statement.strftime('%s'))*1000])
            if n % 28 == 0:
                values.append([
                int(float(data.date_statement.strftime('%s'))*1000),
                float(data.sensor_value)
                ])
            n += 1
        return values

    def get_week_temperatures(self,  host_name, sensor_type='TEMPERATURE',
            from_date=None, to_date=None):
        query = self._session.query(DataSensors)
        values = []
        if to_date is None:
            to_date = datetime.datetime.now()
        if from_date is None:
            #from_date = datetime.datetime(2000, 1, 1)
            from_date = datetime.datetime.now() - datetime.timedelta(days=7)
        n = 0
        for data in query.filter_by(sensor_type=sensor_type,
                host_name=host_name).filter(and_(DataSensors.date_statement <=
                        to_date, DataSensors.date_statement >= from_date,
                        DataSensors.sensor_value != 'NULL')).order_by(DataSensors.date_statement).all():
            #values.append([float(data.sensor_value),
            #    float(data.date_statement.strftime('%s'))*1000])
            if n % 7 == 0:
                values.append([
                    int(float(data.date_statement.strftime('%s'))*1000),
                    float(data.sensor_value)
                    ])
            n += 1
        return values

    def get_day_temperatures(self,  host_name, sensor_type='TEMPERATURE',
            from_date=None, to_date=None):
        query = self._session.query(DataSensors)
        values = []
        if to_date is None:
            to_date = datetime.datetime.now()
        if from_date is None:
            #from_date = datetime.datetime(2000, 1, 1)
            from_date = datetime.datetime.now() - datetime.timedelta(hours=24)
        for data in query.filter_by(sensor_type=sensor_type,
                host_name=host_name).filter(and_(DataSensors.date_statement <=
                        to_date, DataSensors.date_statement >= from_date,
                        DataSensors.sensor_value != 'NULL')).order_by(DataSensors.date_statement).all():
            #values.append([float(data.sensor_value),
            #    float(data.date_statement.strftime('%s'))*1000])
            values.append([
                int(float(data.date_statement.strftime('%s'))*1000),
                float(data.sensor_value)
                ])
        return values

    
class DispatcherApp(object):
    def __init__(self):
        self._data_collector = DataCollector()
        self._data_collector_rpc = JsonRpcApp(self._data_collector) 
        self._mobile = MobileApp() 
        self._index = IndexApp()

    def __call__(self, environ, start_response):
        req = Request(environ)
        if req.method == 'POST':
            return self._data_collector_rpc(environ, start_response)
        else:
            sys.stderr.write(environ['PATH_INFO']+"\n")
            if re.search(r'/get', environ['PATH_INFO']):
                if re.search(r'/get/month', environ['PATH_INFO']):
                    temps = self._data_collector.get_month_temperatures(host_name='Chezjohnny')
                elif re.search(r'/get/week', environ['PATH_INFO']):
                    temps = self._data_collector.get_week_temperatures(host_name='Chezjohnny')
                else:
                    temps = self._data_collector.get_day_temperatures(host_name='Chezjohnny')
                resp = Response(
                    status=200,
                    content_type='application/json',
                    body=dumps(temps))
            elif re.search(r'/mobile', environ['PATH_INFO']):
                return self._mobile(environ, start_response)
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
						<script src="/js/jquery.flot.threshold.multiple.js" type="text/javascript"></script> 
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

class MobileApp(object):
    """
    Serve mobile application
    """
    def __init__(self):
        self._http_header = """
<!DOCTYPE html> 
<html> 
  <head> 
    <title>Relevé de températures</title> 
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1"> 
    <meta name="apple-mobile-web-app-capable" content="yes" />
    <link rel="stylesheet" href="http://code.jquery.com/mobile/1.0.1/jquery.mobile-1.0.1.min.css" />
    <script src="http://code.jquery.com/jquery-1.6.4.min.js"></script>
    <script src="http://code.jquery.com/mobile/1.0.1/jquery.mobile-1.0.1.min.js"></script>
    <meta http-equiv="content-type" content="text/html; charset=utf-8" />
    <script src="/js/jquery.flot.js" type="text/javascript"></script> 
    <script src="/js/jquery.flot.threshold.multiple.js" type="text/javascript"></script> 
    <script src="/js/temperature.js" type="text/javascript"></script> 
    <meta http-equiv="content-type" content="text/html; charset=utf-8" />
    <link rel="stylesheet" href="/css/mobile.css" />
  </head> 
  <body> 

"""
        self._http_footer = """

  </body>
</html>
"""
        self._page_content = """

    <div data-role="page" id="%s">

      <div data-role="header">
        <a href="/rdc/mobile" data-role="button" data-icon="home" data-iconpos="notext"></a>
        <h1>Hello</h1>
        <a href="#config" data-role="button" data-icon="gear" data-iconpos="notext"></a>
      </div><!-- /header -->

      <div data-role="content">	
      %s
      </div><!-- /content -->

      <div data-role="footer" data-position="fixed" data-id="footer">
        <div data-role="navbar">
          <ul>
            <li><a href="mobile/data">Relevés</a></li>
            <li><a href="mobile/info">Informations</a></li>
            <li><a href="mobile/history">Historique</a></li>
          </ul>
        </div><!-- /navbar -->
      </div><!-- /footer -->

    </div><!-- /page -->
"""
    def __call__(self, environ, start_response):
        req = Request(environ)
        try:
            resp = self._process(req)
        except ValueError, e:
            resp = exc.HTTPBadRequest(str(e))
        except exc.HTTPException, e:
            resp = e
        return resp(environ, start_response)
    
    def configuration(self):
        page = """
    <div data-role="page" id="authentification">

      <div data-role="header">
        <a href="/rdc/mobile" data-transition="flip"  data-direction="reverse" data-role="button" data-icon="home"
        data-iconpos="notext"></a>
        <h1>Athentification</h1>
      </div><!-- /header -->

      <div data-role="content">	
          <form action="forms-sample-response.php" method="get" class="ui-body ui-body-a ui-corner-all">
              <fieldset>
                  <div data-role="fieldcontain">
                      <label for="email">Email:</label>
                      <input type="email" name="email" id="email" value=""  />
                      <label for="pass">Mot de passe:</label>
                      <input type="password" name="pass" id="pass" value=""  />
                  </div>
                  <button type="submit" data-theme="b" name="submit" value="submit-value">Submit</button>
               </fieldset>
           </form>
      </div>    

      </div><!-- /content -->
    </div><!-- /page -->
"""
        return self._http_header + page + self._http_footer

    def _mobile(self):
        page = """
    <div data-role="page" id="home">

      <div data-role="header">
        <!--<a href="/rdc/mobile" data-role="button" data-icon="home"
        data-iconpos="notext"></a> -->
        <h1>Hello</h1>
        <a href="/mobile/help" data-role="button" data-icon="info" data-iconpos="notext"></a>
      </div><!-- /header -->

      <div data-role="content">	
        <ul data-role="listview" data-inset="true">
            <li data-role="list-divider">Selection</li>
            <li><a href="mobile/info">Sondes</a></li>        
            <li><a href="mobile/history">Journal</a></li>
            <li><a href="mobile/configuration">Configuration</a></li>
        </ul>
      </div><!-- /content -->

      <!-- <div data-role="footer" data-position="fixed" data-id="footer">
        <div data-role="navbar">
          <ul>
            <li><a href="mobile/data">Relevés</a></li>
            <li><a href="mobile/info">Informations</a></li>
            <li><a href="mobile/history">Historique</a></li>
          </ul>
        </div>
      </div>-->

    </div><!-- /page -->
"""
        return self._http_header + page + self._http_footer

    def data(self):
        page = """
    <div data-role="page" id="dataPage" data-add-back-btn="true">

      <div data-role="header">
        <!--<a href="/rdc/mobile" data-role="button" data-icon="home"
        data-iconpos="notext"></a> -->
        <h1>Relevés de données</h1>
        <div data-role="navbar">
          <ul>
            <li><a href="#" id="day" class="ui-btn-active">Jour</a></li>
            <li><a href="#" id="week">Semaine</a></li>
            <li><a href="#" id="month">Mois</a></li>
          </ul>
        </div>
      </div><!-- /header -->

      <select name="select-choice-0" id="select-choice-1" data-native-menu="false">
         <option value="All">Tous</option>
"""
        data = DataCollector()
        hosts = data.get_hosts()
        for host in hosts:
                page += """
         <option value="%s">%s</option>
""" % (host, host)
        page += """
      </select>
	<div data-role="content">	
	    <div id="data-plot"></div>
	</div><!-- /content -->

      <!-- <div data-role="footer" data-position="fixed" data-id="footer">
        <div data-role="navbar">
          <ul>
            <li><a id="day">Jour</a></li>
            <li><a id="week">Semaine</a></li>
            <li><a id="month">Mois</a></li>
          </ul>
        </div>
      </div>-->

    </div><!-- /page -->
"""
        return self._http_header + page + self._http_footer

    def history(self):
        page = """
    <div data-role="page" id="historyPage" data-add-back-btn="true">

      <div data-role="header">
        <h1>Journal</h1>
      </div><!-- /header -->
      <p>History</p>
    </div><!-- /page -->
"""
        return self._http_header + page + self._http_footer

    def mobile(self):
        data = DataCollector()
        hosts = data.get_hosts()
        import locale
        locale.setlocale(locale.LC_ALL,'fr_CH.UTF-8')
        page = """
    <div data-role="page" id="infoPage">

      <div data-role="header">
        <a href="mobile/configuration" data-transition="flip" data-role="button" data-icon="gear" data-iconpos="notext"></a>
        <h1>Températures des Comby</h1>
      </div><!-- /header -->
	<div data-role="content">	
      <ul data-role="listview">
"""     
        for host in hosts: 
                infos = data.get_infos(host)
                try:
                   temperature_last_date = infos['TEMPERATURE'].date_statement
                   last_temperature_value = infos['TEMPERATURE'].sensor_value
                   last_date = temperature_last_date.strftime('%A %d %B %Y')
                   last_time = temperature_last_date.strftime('%H h %M min %S s')
                   last_balance = infos['BALANCE'].sensor_value
                   last_expiration = infos['EXPIRATION'].sensor_value
                   page += """
          <li data-role="list-divider">%s<span class="ui-li-count">%.1f˚C</span></li>
              <li><a href="mobile/data">
                  <h3>%s</h3>
                  <p><strong>Etat:</strong> activé</p>
                  <p><strong>Solde:</strong>%s, <strong>Expiration:</strong>%s</p>
                  <p class="ui-li-aside"><strong>%s</strong></p>

              </a></li>
""" % (last_date, float(last_temperature_value), host,last_balance,last_expiration, last_time)
                except:
                    pass
        page += """
        </ul>
	</div><!-- /content -->

    </div><!-- /page -->
"""
        return self._http_header + page + self._http_footer
    
    def _process(self, req):
        if not req.method == 'GET':
            raise exc.HTTPMethodNotAllowed(
                "Only GET allowed",
                allowed='GET')
        method = req.path.split('/')[-1]
        if method.startswith('_'):
            raise exc.HTTPForbidden(
                "Bad method name %s: must not start with _" % method)
        try:
            method = getattr(self, method)
        except AttributeError:
            raise ValueError(
                "No such method %s" % method)
        try:
            result = method()
        except:
            text = traceback.format_exc()
            exc_value = sys.exc_info()[1]
            return Response(
                status=500,
                content_type='text/html',
                body="MobileError: %s, error: %s" % (str(exc_value), text))
        return Response(
            content_type='text/html',
            body=result)

    def process(self, req):
        if not req.method == 'GET':
            raise exc.HTTPMethodNotAllowed(
                "Only GET allowed",
                allowed='GET')
        return Response(
            status=200,
            content_type='text/html',
            body="%s" % req.path)

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
