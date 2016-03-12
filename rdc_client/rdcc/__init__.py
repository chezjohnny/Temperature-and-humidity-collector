#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Johnny Mariethoz <chezjohnny@gmail.com>"
__version__ = "0.0.0"
__copyright__ = "Copyright (c) 2009 Johnny Mariethoz"
__license__ = "Internal Use Only"


#---------------------------- Modules -----------------------------------------

# import of standard modules
import sys
import os
import re
from optparse import OptionParser
import serial
from curses import ascii
import datetime

# Hex to dec conversion array
hex2dec = {'0':0, '1':1, '2':2, '3':3,'4':4, '5':5, '6':6, '7':7,'8':8, '9':9, 'A':10, 'B':11, 'C':12, 'D':13, 'E':14, 'F':15 }

# GSM to ISO8859-1 conversion array
gsm_to_latin = {'0':64, '1':163, '2':36, '3':165,'4':232, '5':233, '6':249, '7':236,'8':242, '9':199,
                '11':216, '12':248,
                '14':197, '15':229, '16':0, '17':95,
                '18':0, '19':0, '20':0, '21':0, '22':0, '23':0, '24':0, '25':0, '26':0, '27':0,
                '28':198, '29':230, '30':223, '31':201,
                '36':164,
                '64':161,
                '91':196, '92':214, '93':209, '94':220, '95':167, '96':191,
                '123':228, '124':246, '125':241, '126':252, '127':224}


def hex2int(n):
        """
        Convert a hex number to decimal
        """
        c1 = n[0]
        c2 = n[1]

        c3 = (hex2dec[c1] * 16) + (hex2dec[c2])
        return int("%s" % c3)


def int2hex(n):
        """
        Convert a decimal number to hexadecimal
        """
        hex = ""
        q = n
        while q > 0:
                r = q % 16
                if   r == 10: hex = 'A' + hex
                elif r == 11: hex = 'B' + hex
                elif r == 12: hex = 'C' + hex
                elif r == 13: hex = 'D' + hex
                elif r == 14: hex = 'E' + hex
                elif r == 15: hex = 'F' + hex
                else:
                        hex = str(r) + hex
                q = int(q/16)

        if len(hex) % 2 == 1: hex = '0' + hex
        return hex


def byteSwap(byte):
        """
        Swap the first and second digit position inside a hex byte
        """
        return "%c%c" % (byte[1], byte[0])


def parseTimeStamp(time):
        """
        Convert the time from PDU format to some common format
        """

        y = byteSwap(time[0:2])
        m = byteSwap(time[2:4])
        d = byteSwap(time[4:6])

        hour = byteSwap(time[6:8])
        min = byteSwap(time[8:10])
        sec = byteSwap(time[10:12])

        if int(y) < 70:
                y = "20" + y

        return "%s.%s.%s %s:%s" % (y, m, d, hour, min)


def decodeText7Bit(src):
        """
        Decode the 7-bits coded text to one byte per character
        """

        bits = ''

        i = 0
        l = len(src) - 1

        # First, get the bit stream, concatenating all binary represented chars
        while i < l:
                bits += char2bits(src[i:i+2])
                i += 2

        # Now decode those pseudo-8bit octets
        char_nr = 0
        i = 1

        tmp_out = ''
        acumul = ''
        decoded = ''
        while char_nr <= len(bits):
                byte = bits[char_nr + i:char_nr + 8]
                tmp_out += byte + "+" + acumul + " "
                byte += acumul
                c = chr(bits2int(byte))

                decoded += c

                acumul = bits[char_nr:char_nr + i]

                i += 1
                char_nr += 8

                if i==8:
                        i = 1
                        char_nr
                        decoded += chr(bits2int(acumul))
                        acumul=''
                        tmp_out += "\n"

        return gsm2latin(decoded)


def decodeText8Bit(src):
        """
        Decode the 8-bits coded text to one byte per character
        """
        chars = ''
        i = 0
        while i < len(src):
                chars += chr(src[i:i + 2])
                i += 2
        return chars


def decodeText16Bit(src):
        """
        Decode the 16-bits coded text to one byte per character
        """
        chars = u''
        i = 0
        while i < len(src):
                h1 = src[i:i + 2]
                h2 = src[i + 2:i + 4]
                c1 = hex2int(h1)
                c2 = hex2int(h2)

                unicodeIntChar = (256 * c1) + c2
                unicodeChar = chr(unicodeIntChar)

                chars += unicodeChar
                i += 4
        return chars


def encodeText7Bit(src):
        """
        Encode ASCII text to 7-bit encoding
        """
        result = []
        count = 0
        last = 0
        for c in src:
                this = ord(c) << (8 - count)
                if count:
                        result.append('%02X' % ((last >> 8) | (this & 0xFF)))
                count = (count + 1) % 8
                last = this
        result.append('%02x' % (last >> 8))
        return ''.join(result)


def char2bits(char):
        """
        Convert a character to binary.
        """

        inputChar = hex2int(char)
        mask = 1
        output = ''
        bitNo = 1

        while bitNo <= 8:
                if inputChar & mask > 0:
                        output = '1' + output
                else:
                        output = '0' + output
                mask = mask<<1
                bitNo += 1

        return output


def bits2int(bits):
        """
        Convert a binary string to a decimal integer
        """

        mask = 1
        i = 0
        end = len(bits) - 1

        result = 0
        while i <= end:
                if bits[end - i] == "1":
                        result += mask
                mask = mask << 1
                i += 1

        return result


def gsm2latin(gsm):
        """
        Convert a GSM encoded string to latin1 (where available).
        TODO: implement the extension table introduced by char 27.
        """

        i = 0
        latin = ''
        while i < len(gsm) - 1:
                if str(ord(gsm[i])) in gsm_to_latin:
                        latin += chr(gsm_to_latin[str(ord(gsm[i]))])
                else:
                        latin += gsm[i]
                i += 1

        return latin


def pdu_to_text(text): 
    #result = int2hex(len(text))
    result = encodeText7Bit(text)
    return result





# local modules

class Modem3G(object):
    def __init__(self, config):
        self._device = config.modem.device
        self._speed = config.modem.speed
        self._timeout = config.modem.timeout
        self._pin = config.modem.pin
        self._name = config.host_name
        #self._at_command('AT^CURC=0')
        #self._at_command('AT^U2DIAG=0')
        
    def check_pin(self):
        at_msg = self._at_command('AT+CPIN?')
        for msg in at_msg:
            if msg.startswith('+CPIN: READY'):
                return True
        self._at_command('AT+CPIN="%s"'% self._pin)


    def _at_command(self, command, sleep=0):
        #self._connection.open()
        import time
        self._connection = serial.Serial(self._device, 
                self._speed, timeout=self._timeout,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
		rtscts=True, dsrdtr=True,
                bytesize=serial.EIGHTBITS
                )  # open port
        self._connection.write(command)
        self._connection.write(ascii.ctrl('m'))                        # end session
        #self._connection.close()
        #self._connection.open()
        #res = self._connection.readlines()
        self._connection.flush()
        self._connection.flushInput()
        self._connection.flushOutput()
        if sleep:
            time.sleep(sleep)
        res = []
        while self._connection.inWaiting():
            res.append(self._connection.readline())
        self._connection.close()
        return res

    def _get_ussd(self, number):
        """Balance: *130#
           Expiration: *130*101#
        """
        self._at_command('ATZ\r')
        #self._connection.write('ATZ')
        #self._connection.write(ascii.ctrl('m'))                        # end session
        self._at_command('AT^CURC=0\r')
        at_msg = self._at_command('AT+CUSD=1, "%s", 15\r\n' %
                pdu_to_text(number), 3)
        to_return = None
        for msg in at_msg:
            if msg.startswith('+CUSD'):
                tmp_to_return =  msg.split('"')[1]
                tmp_to_return = decodeText7Bit(tmp_to_return)#.decode('latin1')
                regexp = re.search(r'Fr.\s+(.*?)\.', tmp_to_return)
                if regexp:
                    tmp_to_return = regexp.group(1)
                to_return = tmp_to_return
        self._at_command('AT^CURC=1\r')
        return to_return

    def get_info(self):
        s = self._data.select()
        rs = s.execute()
        
        to_return = {}
        for row in rs:
            to_return.setdefault(row.name, []).append([row.balance,
                row.expiration,
            row.datetime.strftime("%s")])
        return to_return

    def get_balance(self):
        return self._get_ussd("*130#")

    def get_expiration_date(self):
        return self._get_ussd("*130*101#")

    def get_all_sms(self, force_all=False):
        _filter = "REC UNREAD"
        if force_all:
            _filter = "ALL"
        self._at_command('AT+CMGF=1\r\n')
        results = self._at_command('AT+CMGL="%s"\r\n' % _filter)
        to_return = []
        while results:
            res = results.pop(0)
            if res.startswith('+CMGL:'):
                phone = res.split(',')[2].replace('"','')
                status = res.split(',')[1].replace('"','')
                tmp = results.pop(0)
                msg = tmp
                while tmp and not tmp.startswith('OK') and not results[0].startswith('+CMGL:'):
                    tmp = results.pop(0)
                    if tmp.startswith('OK') or results[0].startswith('+CMGL:'):
                        break
                    else:
                        msg += tmp
                to_return.append((phone, status, msg))
        return to_return
    
    def send_sms(self, message, telephoneNumber):
        """Send a SMS"""
        #self._connection.open()
        self._connection = serial.Serial(self._device, self._speed, timeout=self._timeout)  # open port
        self._connection.write('AT+CMGF=1\r\n')
        self._connection.write('AT+CMGS="%s"\r\n' % telephoneNumber)
        self._connection.write(ascii.ctrl('m'))                        # end session
        self._connection.write(message)                                # message
        self._connection.write(ascii.ctrl('z'))                        # end session
        #self._connection.open()
        res = self._connection.readlines()
        self._connection.close()
        self._connection = None
        return res


