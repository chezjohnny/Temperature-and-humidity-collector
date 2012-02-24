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
import json
import datetime
import daemon
import lockfile
import time
from config import Config
from rdcc import Modem3G
import datetime
from datetime import datetime
from datetime import timedelta

import ow
import smtplib
import xmlrpclib

# third party modules


# local modules

def info(msg):
    now = datetime.now()
    print "%s: %s" % (now, msg)
    sys.stdout.flush()

class Email(object):
    def __init__(self, config):
        self._user = config.email.smtp.username
        self._passwd = config.email.smtp.password
        self._port = config.email.smtp.port
        self._host = config.email.smtp.host
        self._from = config.email.add_from
        self._to = config.email.add_to
    def send(self, subject, body):
        smtpserver = smtplib.SMTP(self._host, self._port)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo
        smtpserver.login(self._user, self._passwd)
        header = 'To:' + self._to + '\n' + 'From: ' + self._from + '\n' + 'Subject:' + subject + '\n'
        msg = header + '\n' + body
        smtpserver.sendmail(self._from, self._to, msg)
        smtpserver.close()

class TemperatureSensor(object):
    def __init__(self, sensor_type='DS18S20'):
        self._sensor_type = sensor_type
        #ow.init('u')
    def temperature(self):
        root = ow.Sensor( '/' )
        to_return = None
        for sensor in root.find(type=self._sensor_type):
            to_return = float(sensor.temperature)
        return to_return
    def close(self):
        pass


def post_temperature(config):
    temp = TemperatureSensor(sensor_type=config.sensor.type)
    try:
        temp_value = temp.temperature()
    except:
        ow.init('u')
        info("Try to re-init")
        date = datetime.now()
        err_msg = "%s: %s %s\n" % (date, type(e), str(e))
        sys.stderr.write(err_msg)
        sys.stderr.flush()
        temp_value = temp.temperature()

    to_return = post_data(config.host_name, config.server_address, temp_value, 'TEMPERATURE')
    temp.close()
    return to_return

def post_balance(config):
    modem = Modem3G(config)
    temp_value = modem.get_balance()
    to_return = post_data(config.host_name, config.server_address, temp_value, 'BALANCE')
    return to_return

def post_expiration_date(config):
    modem = Modem3G(config)
    temp_value = modem.get_expiration_date()
    to_return = post_data(config.host_name, config.server_address, temp_value,
            'EXPIRATION')
    return to_return

def post_data(host_name, server_address, sensor_value, sensor_type):
    server = xmlrpclib.ServerProxy(server_address)
    now = datetime.now().isoformat()
    server.add_data(host_name, now, sensor_value, sensor_type)

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

    if len(args) != 1:
        parser.error("Error: incorrect number of arguments, try --help")

    cfg = Config(args[0])
    email = Email(cfg)
    log_dir = cfg.log_dir
    try:
        os.mkdir(log_dir)
    except OSError:
        pass
    if options.daemon:
        with daemon.DaemonContext(working_directory='/',
                pidfile=lockfile.FileLock(os.path.join(log_dir,'temperature.pid')),
                stdout=file(os.path.join(log_dir,'temperature.log'),'a'),
                stderr=file(os.path.join(log_dir,'temperature.err'), 'a')):
            
            ow.init('u')
            now = datetime.now()
            temperature_interval = timedelta(minutes=cfg.interval.temperature)
            info_interval = timedelta(minutes=cfg.interval.info)
            error_interval = timedelta(minutes=cfg.interval.error)
            last_temp = now - temperature_interval
            last_info = now - info_interval
            last_error = now - error_interval
            errors = []
            while True:
                try:
                    info("Try to collect data")
                    if (datetime.now()-temperature_interval) >= last_temp :
                        info("Try to collect temperature")
                        post_temperature(cfg)
                        info("Temperature done")
                        last_temp = datetime.now()
                    if (datetime.now()-info_interval) >= last_info :
                        info("Try to collect balance")
                        post_balance(cfg)
                        info("Balance done")
                        info("Try to collect expiration date")
                        post_expiration_date(cfg)
                        info("Expiration done")
                        last_info = datetime.now()
                except Exception, e:
                    date = datetime.now()
                    err_msg = "%s: %s %s\n" % (date, type(e), str(e))
                    sys.stderr.write(err_msg)
                    sys.stderr.flush()
                    errors.append(err_msg)
                        
                    if (datetime.now()-error_interval) >= last_error :
                        info("Send email with %s" % "\n".join(errors))
                        try:
                            email.send("Erreur de %s" % cfg.host_name, "\n".join(errors))
                        except:
                            date = datetime.now()
                            err_msg = "%s: %s %s\n" % (date, type(e), str(e))
                            sys.stderr.write(err_msg)
                            sys.stderr.flush()
                        last_error = datetime.now()
                        errors = []
                info("Sleep for one minute")
                time.sleep(60)

    else:
        for i in range(2):
            print "Collect"
            import ow
            ow.init('u')
            temp = TemperatureSensor(sensor_type=cfg.sensor.type)
            print temp.temperature()
            post_temperature(cfg)
            time.sleep(10)
        #post_balance(cfg)
        #post_expiration_date(cfg)
