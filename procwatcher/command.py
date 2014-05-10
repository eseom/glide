#!/usr/bin/env python
#
# author: EunseokEom <me@eseom.org>

import socket
import time

class Command(object):
    def __init__(self, host):
        self.host = host

    def command(self, command, procname):
        try:
            self.socket = socket.create_connection((self.host, 32767))
        except:
            pass
        try:
            self.socket.send('%s %s' % (command, procname,))
        except:
            pass
        try:
            self.socket.close()
        except:
            pass

if __name__ == '__main__':
    c = Command('localhost')
    c.command('stop', 'proc1')
    c.command('stop', 'proc2')
    time.sleep(10)
    c.command('quit', 'procwatcher')
