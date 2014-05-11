#!/usr/bin/env python
#
# author: EunseokEom <me@eseom.org>

import socket
import time
import sys
import optparse

class RESULT(object):
    SUCCESS = '1'
    FAIL    = '0'

class Command(object):
    def __init__(self, host):
        self.host = host

    def _command(self, cmd, procname):
        try:
            sock = socket.create_connection((self.host, 32767))
        except Exception as e:
            return -1
        try:
            sock.send('%s %s' % (cmd, procname,))
            message = sock.recv(1024)
        except Exception as e:
            pass
        try:
            sock.close()
            return message
        except:
            pass

    @classmethod
    def command(cls, argv):
        cmd = argv[0]
        procname = ' '.join(argv[1:])
        if cmd not in ('start', 'restart', 'stop', 'hangup', 'alarm', 'status',):
            print 'no such command: %s' % cmd
            sys.exit(2)
        result = cls('localhost')._command(cmd, procname)
        if result == '1':
            result = True
        elif result == '0':
            result = False
        if result == -1:
            print 'cannot connect master process. is procwatchd running?'
            sys.exit(1)
        if cmd == 'start':
            if result:
                print 'started [%s]' % procname
                return True
            else:
                print '[%s] cannot be started now' % (procname,)
                return False
        elif cmd == 'restart':
            if result:
                print 'restarted [%s]' % procname
                return True
            else:
                print '[%s] cannot be restarted now' % (procname,)
                return False
        elif cmd == 'stop':
            if result:
                print 'stopped [%s]' % procname
                return True
            else:
                print '[%s] cannot be stopped' % (procname,)
                return False
        elif cmd == 'hangup':
            if result:
                print 'hung up [%s]' % procname
                return True
            else:
                print '[%s] cannot be hung up' % (procname,)
                return False
        elif cmd == 'alarm':
            if result:
                print 'alarmed [%s]' % procname
                return True
            else:
                print '[%s] cannot be alarmed' % (procname,)
                return False
        elif cmd == 'status':
            return result
        else:
            print 'no such command: %s' % cmd

def main():
    parser = optparse.OptionParser()
    _, argv = parser.parse_args()
    if len(argv) < 2:
        if argv[0] == 'status':
            argv.append('*')
        else:
            print 'usage: pwctl <command> <process name>'
            sys.exit(1)
    result = Command.command(argv)
    if argv[0] == 'status':
        print result
