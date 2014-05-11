#!/usr/bin/env python
#
# author: EunseokEom <me@eseom.org>

import socket
import time

class RESULT(object):
    SUCCESS = '1'
    FAIL    = '0'

class Command(object):
    def __init__(self, host):
        self.host = host

    def command(self, command, procname):
        try:
            sock = socket.create_connection((self.host, 32767))
        except Exception as e:
            print e
        try:
            sock.send('%s %s' % (command, procname,))
            message = sock.recv(1024)
        except Exception as e:
            print e
            pass
        try:
            sock.close()
            return message
        except:
            pass
