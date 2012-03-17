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

import subprocess
import ow
import smtplib
import xmlrpclib
import socket
from email.MIMEText import MIMEText

from easyprocess import EasyProcess
# third party modules

#----------------- Exceptions -------------------
class SensorError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class TimeoutError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class CmdError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

# local modules

class Email(object):
    """ To send email """
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
        for _to in self._to:
            msg = MIMEText(body)        # won't work
            msg['From'] = self._from        # won't work
            msg['To'] = _to       # won't work
            msg['Subject'] = subject
            smtpserver.sendmail(self._from, self._to, msg.as_string())
        smtpserver.close()

class TemperatureSensor(object):
    """ To collect temperature"""
    def __init__(self, sensor_type='DS18S20'):
        self._sensor_type = sensor_type
        #ow.init('u')
    def temperature(self):
        root = ow.Sensor( '/' )
        to_return = None
        for sensor in root.find(type=self._sensor_type):
            to_return = float(sensor.temperature)
        return to_return

def info(msg):
    """ Just a function to print message """
    now = datetime.now()
    print "%s: %s" % (now, msg)
    sys.stdout.flush()

def post_temperature(config):
    """Send temperature to the server."""
    temp = TemperatureSensor(sensor_type=config.sensor.type)
    n = 3
    while n:
        try:
            temp_value = temp.temperature()
            if temp_value is not None:
                post_data(config.host_name, config.server_address, temp_value, 'TEMPERATURE')
            else:
                raise SensorError("température")
            break
        except Exception, e:
            n -= 1
            info("Temperature collection failed, retry!")
            if n == 0:
                raise

def post_balance(config):
    """Send the 3G balance value to the server"""
    modem = Modem3G(config)
    temp_value = modem.get_balance()
    to_return = post_data(config.host_name, config.server_address, temp_value, 'BALANCE')
    return to_return

def post_expiration_date(config):
    """Send the 3g key expiration date to the server."""
    modem = Modem3G(config)
    temp_value = modem.get_expiration_date()
    to_return = post_data(config.host_name, config.server_address, temp_value,
            'EXPIRATION')
    return to_return

def post_data(host_name, server_address, sensor_value, sensor_type):
    """Post sensor values to the server"""
    server = xmlrpclib.ServerProxy(server_address)
    now = datetime.now().isoformat()
    print server.add_data(host_name, now, sensor_value, sensor_type)


def sub_command(cmd_str, timeout=30):
    """Run a command as child process using a timeout"""
    cmd = EasyProcess(cmd_str)
    cmd.call(timeout=timeout)
    if cmd.timeout_happened:
        raise TimeoutError("Erreur lors de la commande: %s, temps de réponse "\
                "trop long." % cmd_str)
    if cmd.return_code or cmd.oserror or cmd.timeout_happened:
        raise CmdError("Erreur lors de la commande: %s, la commande retourne "\
                "(%s, %s)." % (cmd_str, cmd.stderr, cmd.stdout))
    return cmd.stdout

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
    parser.add_option ("-i", "--info", dest="info",
                               help="post information",
                               action="store_true",
                               default=False)

    parser.add_option ("-t", "--temperature", dest="temperature",
                               help="post temperature value",
                               action="store_true",
                               default=False)
    parser.add_option ("-s", "--subprocess", dest="subprocess",
                               help="test subprocess",
                               action="store_true",
                               default=False)
    (options,args) = parser.parse_args ()

    if len(args) != 1:
        parser.error("Error: incorrect number of arguments, try --help")

    #configuration
    cfg = Config(args[0])
    
    #to send alert email
    email = Email(cfg)

    #log directory
    log_dir = cfg.log_dir
    try:
        os.mkdir(log_dir)
    except OSError:
        pass

    #actual script path
    script_path = sys.argv[0]

    #Unix daemon mode
    if options.daemon:
        with daemon.DaemonContext(working_directory='/',
                pidfile=lockfile.FileLock(os.path.join(log_dir,'temperature.pid')),
                stdout=file(os.path.join(log_dir,'temperature.log'),'a'),
                stderr=file(os.path.join(log_dir,'temperature.err'), 'a')):
            
            #time intervals to check when we have to collect data or send
            #alerts
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
                        msg = sub_command("%s -t %s" % (script_path, args[0]),
                                cfg.cmd.timeout)
                        info('Result: %s' % msg)
                        info("Temperature done")
                        last_temp = datetime.now()

                    if (datetime.now()-info_interval) >= last_info :
                        info("Try to collect informations")
                        msg = sub_command("%s -i %s" % (script_path, args[0]),
                                cfg.cmd.timeout)
                        info("Information done")
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
        if options.temperature:
            try:
                ow.init('u')
                temp = TemperatureSensor(sensor_type=cfg.sensor.type)
                post_temperature(cfg)
            except ow.exNoController:
                print "L'adaptateur USB 1-Wire n'est pas connecté"
                sys.exit(1)
            except SensorError as e:
                print "La sonde de %s n'est pas connectée." % e.value
                sys.exit(1)
            except xmlrpclib.ProtocolError:
                print "Le serveur est mal configuré."
                sys.exit(1)
            except socket.gaierror:
                print "Le serveur est mal configuré."
                sys.exit(1)
            except socket.error:
                print "Le serveur ne répond pas."
                sys.exit(1)
            except Exception as e:
                print "Une erreur inconnue est survenue: %s: %s\n" % (type(e), str(e))
                sys.exit(1)

        elif options.info:
            import serial.serialutil
            try:
                post_balance(cfg)
                post_expiration_date(cfg)
            except serial.serialutil.SerialException:
                print "Erreur: la clé 3G n'est pas connectée."
                sys.exit(1)
            except xmlrpclib.ProtocolError:
                print "Le serveur est mal configuré."
                sys.exit(1)
            except socket.gaierror:
                print "Le serveur est mal configuré."
                sys.exit(1)
            except socket.error:
                print "Le serveur ne répond pas."
                sys.exit(1)
            except Exception as e:
                print "Une erreur inconnue est survenue: %s: %s\n" % (type(e), str(e))
                sys.exit(1)
