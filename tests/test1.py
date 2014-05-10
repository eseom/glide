import sys
import io
import unittest
import os
import time
import threading

from procwatcher.watcher import Proc, Daemon
from procwatcher.command import Command

CFGFILE = 'test.conf'

class TestCase(unittest.TestCase):
    def run_server(self):
        print 
        print '(I) this test takes around about 30 seconds at least.'
        print '(I) procwatcher is running now.'
        returned_data = {}
        def callback(message):
            if message.procname not in returned_data.keys():
                returned_data[message.procname] = []
            returned_data[message.procname].append(message.message)
        daemon = Daemon(CFGFILE, message_callback=callback)
        daemon.start()

        # daemon stopped
        return returned_data

    def run_client(self):
        time.sleep(3)
        print '(I) a client was executed that restart [output proc2].'
        Command('localhost').command('restart', 'output proc2')
        time.sleep(3)
        print '(I) a client was executed that stops [output proc1].'
        Command('localhost').command('stop', 'output proc1')
        time.sleep(7)
        print '(I) a client was executed that stops the running procwatcher.'
        Command('localhost').command('quit', 'procwatcher')

    def test_loop(self):
        client_thread = threading.Thread(target=self.run_client)
        client_thread.start()
        returned_from_server = self.run_server()
        client_thread.join()

        for k, v in returned_from_server.items():
            assert ''.join(v[len(v) - 7:]) == '#' * 7

    def test_get_procs(self):
        assert 3 == len(Proc.get_procs(CFGFILE))

    def setUp(self):
        d = os.path.dirname(os.path.abspath(__file__))
        with open(CFGFILE, 'w') as fp:
            config = """
[output proc1]
path = /bin/bash """ + d + """/outputd.sh 1 6 0.07

[output proc2]
path = /bin/bash """ + d + """/outputd.sh 2 13 0.2

[output proc3]
path = /bin/bash """ + d + """/outputd.sh 3 5 0.3
""".strip(' ')
            fp.write(config)

    def tearDown(self):
        os.remove(CFGFILE)

def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
