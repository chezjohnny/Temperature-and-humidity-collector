#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Johnny Mariethoz <Johnny.Mariethoz@rero.ch>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2009 Rero, Johnny Mariethoz"
__license__ = "Internal Use Only"


#---------------------------- Modules -----------------------------------------

# import of standard modules
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
from optparse import OptionParser
import json
import datetime
import daemon
#import lockfile
import daemon.pidfile
import time
from config import Config
from rdcc import Modem3G
import datetime
from datetime import datetime
from datetime import timedelta

import ow
import smtplib
import xmlrpclib
import socket
from email.MIMEText import MIMEText

from easyprocess import EasyProcess
# third party modules
REBOOT_CMD = EasyProcess("sudo reboot -n -p")


#----------------- Exceptions -------------------
class SensorError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value

class TimeoutError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value

class CmdError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value

# local modules
def wakeup_network(host_name, n=20):
    return 1
    import ping
    success = -1
    for n in range(20):
        res = ping.do_one(host_name, 1, 1)
        if res is not None:
            success = n
            break
    return success

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
        wakeup_network("rdc.mariethoz.net")
        if self._host == "localhost":
            smtpserver = smtplib.SMTP(self._host)
        else:
            smtpserver = smtplib.SMTP(self._host, self._port)
            smtpserver.ehlo()
            smtpserver.starttls()
            smtpserver.ehlo
            smtpserver.login(self._user, self._passwd)
        for _to in self._to:
            msg = MIMEText(body,"plain", "utf-8")        # won't work
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

def info(msg, verbose=False):
    if not verbose:
        return
    """ Just a function to print message """
    now = datetime.now()
    print "%s: %s" % (now, msg)
    sys.stdout.flush()

def post_boot(config):
    info("Post boot data", config.debug)
    post_data(config.host_name, config.server_address, "",
                        'BOOT', verbose=config.debug)
def post_voltage(config):
    info("Post voltage data", config.debug)
    val = int(file("/sys/devices/platform/omap/tsc/ain1").read())/4096. * 1.8 * 11
    post_data(config.host_name, config.server_address, val,
                        'VOLTAGE', verbose=config.debug)

def post_temperature(config):
    """Send temperature to the server."""
    info("Collect temperature", config.debug)
    temp = TemperatureSensor(sensor_type=config.sensor.type)
    info("Temperature collected%s" % temp, config.debug)
    n = 3
    while n:
        temp_value = None
        info("Try to send data %s/%s" % (n-2, n), config.debug)
        try:
            temp_value = temp.temperature()
            if temp_value is not None:
                post_data(config.host_name, config.server_address, temp_value,
                        'TEMPERATURE', verbose=config.debug)
            else:
                raise SensorError("température")
            break
        except Exception, e:
            n -= 1
            info("Temperature collection failed, retry!", config.debug)
            time.sleep(3)
            if n == 0:
                if temp_value is not None and \
                    float(temp_value) <= config.alert.value:
                    modem = Modem3G(config)
                    number = config.alert.sms
                    msg = "Alert: " + config.host_name
                    msg += """
La temperature (%.3f inferieure a (%.3f) et le serveur ne repond pas.
""" % (float(temp_value), config.alert.value)
                    info("Send sms to %s: %s" % (number, msg), config.debug)
                    modem.send_sms(msg, number)
                raise

def post_balance(config):
    """Send the 3G balance value to the server"""
    modem = Modem3G(config)
    to_return = None
    n = 3
    while n:
        temp_value = None
        try:
            temp_value = modem.get_balance()
            if temp_value is not None:
                to_return = post_data(config.host_name, config.server_address, temp_value,
                        'BALANCE', verbose=config.debug)
            else:
                raise SensorError("Balance value is None")
            break
        except Exception, e:
            n -= 1
            info("Balance collection failed, retry!", config.debug)
            if n == 0:
                raise
    return to_return if to_return else "Unknown"

def post_expiration_date(config):
    """Send the 3g key expiration date to the server."""
    modem = Modem3G(config)
    to_return = None
    n = 3
    while n:
        temp_value = None
        try:
            temp_value = modem.get_expiration_date()
            if temp_value is not None:
                to_return = post_data(config.host_name, config.server_address, temp_value,
                    'EXPIRATION', verbose=config.debug)
                break
        except Exception, e:
            n -= 1
            info("Expiration date collection failed, retry!", config.debug)
            if n == 0:
                raise
    return to_return if to_return else "Unknown"

def post_data(host_name, server_address, sensor_value, sensor_type,
        verbose=False):
    """Post sensor values to the server"""
    now = datetime.now().isoformat()
    info("Try to wakup the network", verbose)
    wakeup_network("rdc.mariethoz.net")
    info("Network ready", verbose)
    server = xmlrpclib.ServerProxy(server_address)
    info("Server connected, send data", verbose)
    msg = server.add_data(host_name, now, sensor_value, sensor_type)
    info(msg, verbose)


def sub_command(cmd_str, timeout=30, debug=False):
    """Run a command as child process using a timeout"""
    n = 3
    while n:
        cmd = EasyProcess(cmd_str)
        cmd.call(timeout=timeout)
        if cmd.timeout_happened:
            info("Command failed due to timeout, retry!", debug)
            if n == 1:
                raise TimeoutError(u"Erreur lors de la commande: %s, temps de réponse "\
                    "trop long." % cmd_str)
            n -= 1
        elif cmd.return_code or cmd.oserror:
            info("Command failed due unknown error, retry!", debug)
            if n == 1:
                raise CmdError(u"%s" % (cmd.stderr.decode('utf-8', errors='ignore')))
            n -= 1
        else:
            break
    return cmd.stdout

#---------------------------- Main Part ---------------------------------------

if __name__ == '__main__':

    usage = "usage: %prog [options]"

    parser = OptionParser(usage)

    parser.set_description ("Deamon to collect 1wire data and send to a remote server")

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
    
    parser.add_option ("-b", "--boot", dest="boot",
                               help="post boot",
                               action="store_true",
                               default=False)

    parser.add_option ("-t", "--temperature", dest="temperature",
                               help="post temperature value",
                               action="store_true",
                               default=False)

    parser.add_option ("-c", "--check", dest="check",
                               help="check that rdc is running if the USB 3g key is plugged",
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
    info("Debug", cfg.debug)

    #Unix daemon mode
    pid_file = os.path.join(log_dir,'temperature.pid.lock')
    if options.daemon:
        with daemon.DaemonContext(working_directory='/',
            pidfile=daemon.pidfile.PIDLockFile(pid_file),
            #pidfile=lockfile.FileLock(os.path.join(log_dir,'temperature.pid')),
            stdout=file(os.path.join(log_dir,'temperature.log'),'a'),
            stderr=file(os.path.join(log_dir,'temperature.err'), 'a')):

            #time intervals to check when we have to collect data or send
            #alerts
            info("Debug", cfg.debug)
            import uptime
            now = uptime.uptime()
            temperature_interval = int(cfg.interval.temperature)*60.
            info_interval = None
            if cfg.interval.info:
                info_interval = int(cfg.interval.info)*60.
                last_info = now - info_interval
            error_interval = int(cfg.interval.error)*60.
            last_temp = now - temperature_interval
            last_error = now - error_interval
            errors = []
            info("Debug: now: %s last_temp: %s last_error: %s" %(now, last_temp, last_error), cfg.debug)
            first = True
            while True:
                try:
                    if first:
                        msg = sub_command("%s -b %s" % (script_path, args[0]),
                                timeout=cfg.cmd.timeout, debug=cfg.debug)
                        first = False
                        info("Boot done : %s", (cfg.debug,
                            datetime.datetime.now()))
                except:
                    pass
                try:
                    info("Try to collect data", cfg.debug)
                    info("Debug: now: %s last_temp: %s last_temp: %s" %(now, temperature_interval, last_temp), cfg.debug)

                    if (uptime.uptime()-temperature_interval) >= last_temp :
                        info("Try to collect temperature", cfg.debug)
                        msg = sub_command("%s -t %s" % (script_path, args[0]),
                                timeout=cfg.cmd.timeout, debug=cfg.debug)
                        info('Result: %s' % msg, cfg.debug)
                        info("Temperature done", cfg.debug)
                        last_temp = uptime.uptime()

                    
                    if info_interval and (uptime.uptime()-info_interval) >= last_info :
                        info("Try to collect informations")
                        msg = sub_command("%s -i %s" % (script_path, args[0]),
                                timeout=cfg.cmd.timeout, debug=cfg.debug)
                        info("Information done", cfg.debug)
                        last_info = uptime.uptime()
                except TimeoutError, e:
                    try:
                        info("rebooting...")
                        date = datetime.now()
                        err_msg = "%s: Rebooting due to timeout\n" % (date)
                        sys.stderr.write(err_msg)
                        sys.stderr.flush()
                    except:
                        pass
                    time.sleep(3)
                    REBOOT_CMD.call()
                except Exception, e:
                    date = datetime.now()
                    err_msg = "%s\n\n%s\n%s" % (e, date, type(e))
                    sys.stderr.write(err_msg)
                    sys.stderr.flush()
                    errors.append(err_msg)
                        
                    if (uptime.uptime()-error_interval) >= last_error :
                        info("Send email with %s" % "\n".join(errors),
                                cfg.debug)
                        try:
                            email.send("Erreur de %s" % cfg.host_name, "\n".join(errors))
                        except:
                            date = datetime.now()
                            err_msg = "%s: %s %s\n" % (date, type(e), str(e))
                            sys.stderr.write(err_msg)
                            sys.stderr.flush()
                        last_error = uptime.uptime()
                        errors = []
                info("Sleep for one minute", cfg.debug)
                time.sleep(60)

    else:
        if options.temperature:
            try:
                ow.init('u')
                temp = TemperatureSensor(sensor_type=cfg.sensor.type)
                #print temp.temperature()
                post_temperature(cfg)
            except ow.exNoController:
                sys.stderr.write("L'adaptateur USB 1-Wire n'est pas connecté\n")
                sys.exit(1)
            except SensorError as e:
                sys.stderr.write("La sonde de %s n'est pas connectée.\n" % e.value)
                sys.exit(1)
            except xmlrpclib.ProtocolError:
                sys.stderr.write("Le serveur est mal configuré.\n")
                sys.exit(1)
            except socket.gaierror:
                sys.stderr.write("Le serveur est mal configuré.\n")
                sys.exit(1)
            except socket.error:
                sys.stderr.write("Le serveur ne repond pas.\n")
                sys.exit(1)
            except Exception as e:
                sys.stderr.write("Une erreur inconnue est survenue: %s: %s\n" % (type(e), str(e)))
                sys.exit(1)
            try:
                post_voltage(cfg)
            except:
                pass

        elif options.info:
            import serial.serialutil
            try:
                post_balance(cfg)
                post_expiration_date(cfg)
            except serial.serialutil.SerialException:
                sys.stderr.write("Erreur: la cle 3G n'est pas connectée.\n")
                sys.exit(1)
            except xmlrpclib.ProtocolError:
                sys.stderr.write("Le serveur est mal configuré.\n")
                sys.exit(1)
            except socket.gaierror:
                sys.stderr.write("Le serveur est mal configuré.\n")
                sys.exit(1)
            except socket.error:
                sys.stderr.write("Le serveur ne repond pas.\n")
                sys.exit(1)
            except Exception as e:
                sys.stderr.write("Une erreur inconnue est survenue: %s: %s\n" % (type(e), str(e)))
                sys.exit(1)
        
        elif options.boot:
            try:
                post_boot(cfg)
            except:
                pass
        elif options.check:
            def check():
                if os.path.exists(cfg.modem.device):
                    pass
                    #info('modem is plugged', cfg.debug)
                else:
                    info('modem is unplugged', cfg.debug)
                    return True
                if os.path.isfile(pid_file):
                    #info('pid file exists', cfg.debug)
                    pid = open(pid_file, 'r').read().rstrip()
                    #info('pid: %s' % pid, cfg.debug)
                    if os.path.exists('/proc/%s' % pid):
                        #info('pid (%s) is running' % pid, cfg.debug)
                        return True
                return False
            if not check():
                info("retrying in 5 min", cfg.debug)
                time.sleep(60*5)
                if not check():
                    info("rebooting...", cfg.debug)
                    os.system('sudo reboot -n -p')
