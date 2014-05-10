import sys
import io
import unittest
import os
import datetime
import select
import logging
import socket
import signal
import math
import time
import traceback
import ConfigParser

from multiprocessing import Process

from procwatcher.watcher import Watcher, Proc, Daemon, prepare_socket

CFGFILE = 'test.conf'

print Daemon

class TestCase(unittest.TestCase):
    def test_loop(self):
        def callback(message):
            print message
        daemon = Daemon(CFGFILE, message_callback=callback)
        daemon.start()

    def ttest_start_one(self):
        watcher = Watcher()
        ps = Proc.get_procs(CFGFILE)
        data = []
        for k in ps.keys():
            watcher.start(k, ps[k])
            break
        j = 0
        while True:
            try:
                io, oo, eo = select.select(watcher.rpis, [], [], 0.5)
            except select.error as e:
                pass
            if io:
                j += 1
            for i in io:
                try: data.append(os.read(i, 1024).strip())
                except: pass
            if not watcher.rpis:
                break
            if j == 4:
                break
        assert ['1-1', '1-2', '1-3', '1-4'] == data

    def ttest_get_procs(self):
        assert 2 == len(Proc.get_procs(CFGFILE))

    def setUp(self):
        d = os.path.dirname(os.path.abspath(__file__))
        with open(CFGFILE, 'w') as fp:
            config = """
[proc1]
path = /bin/bash """ + d + """/testdaemon1.sh 20

[proc2]
path = /bin/sh """ + d + """/testdaemon2.sh 10

[proc3]
path = /bin/bash """ + d + """/testdaemon3.sh 30
""".strip(' ')
            fp.write(config)

    def tearDown(self):
        os.remove(CFGFILE)

def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
