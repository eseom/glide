import unittest
import threading
import os
import time
import asyncore
from glide.watcher import Watcher


class Tester(unittest.TestCase):
    def setUp(self):
        self.data = []
        self.daemon_file = 'output.sh'
        daemon_code = """
#!/bin/bash
if test "$#" -ne 3
then
    echo 'usage: bash outputd.sh <identifier number> <loop count> <sleep>'
    exit 1
fi
trap 'for i in $(seq 1 3); do echo "$1-#"; sleep 0.2; done; exit' SIGTERM SIGHUP
for i in `seq 1 $2`; do
    echo "$1-$i"
    sleep $3
done
"""
        with open(self.daemon_file, 'w') as fp:
            fp.write(daemon_code)

        self.cfg_file = 'test.conf'
        c = []
        c.append("""[output proc0]
path = /bin/bash """ + self.daemon_file + """ 0 60 1""")
        c.append("""[output proc1]
path = /bin/bash """ + self.daemon_file + """ 1 130 1""")
        c.append("""[output proc2]
path = /bin/bash """ + self.daemon_file + """ 2 50 1""")
        with open(self.cfg_file, 'w') as fp:
            fp.write('\n'.join(c))

    def tearDown(self):
        try:
            os.remove(self.daemon_file)
            os.remove(self.cfg_file)
        except:
            pass

    def get_watcher(self):
        watcher = Watcher(self.blast_module)
        watcher.match_procs(self.cfg_file)
        return watcher

    def start_procs(self):
        self.watcher.start_all()
        asyncore.loop()

    def ttest_start_procs(self):
        self.watcher = self.get_watcher()
        ct_thread = threading.Thread(target=self.stop_ct)
        ct_thread.start()
        self.start_procs()
        ct_thread.join()

    def stop_ct(self):
        time.sleep(2)
        for x in self.watcher.get_procs():
            x.stop()

    def restart_ct(self):
        time.sleep(2)
        proc = self.watcher.get_procs()[0]
        result, message = self.watcher.stop(proc.name)
        self.assertTrue(result)
        self.assertEquals(message, '')
        time.sleep(6)
        result, message = self.watcher.start(proc.name)
        self.assertFalse(result)
        self.assertEquals(message, 'already operating')
        time.sleep(3)
        result, message = self.watcher.restart(proc.name)
        self.assertFalse(result)
        self.assertEquals(message, 'not running')
        time.sleep(2)  # signal break sleep
        time.sleep(5)
        self.stop_ct()

    def blast_module(self, message, index):
        self.data.append(message.message)

    def test_match_procs(self):
        watcher = self.get_watcher()
        self.assertEquals(len(watcher.nam_map.values()), 3)
        for k, v in watcher.nam_map.items():
            self.assertTrue(k.startswith('output proc'))
            self.assertIn('READY', str(v))

    def test_restart_procs(self):
        self.watcher = self.get_watcher()
        ct_thread = threading.Thread(target=self.restart_ct)
        ct_thread.start()
        self.start_procs()
        ct_thread.join()
