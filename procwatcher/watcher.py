#!/usr/bin/env python
#
# http://github.com/eseom/procwatcher
#
# @author:  EunseokEom <me@eseom.org>
# @desc:    process wrapper with the python asyncore module

import unittest
import threading
import os
import time
import datetime
import signal
import asyncore as async

from multiprocessing import Process

from command import RESULT
from process import Process, STATUS
from config import Config

CFGFILE = '/etc/procwatcher.conf'

class Watcher(object):
    def __init__(self, bm):
        self.bm =      bm
        self.nam_map = {} # key: proc name, value: proc
        self.pid_map = {} # key: proc pid,  value: proc
        signal.signal(signal.SIGCHLD, self.proc_exit)
        # set pgid of the main process
        os.setpgid(os.getpid(), os.getpid())

    def match_procs(self, cfg_file=None):
        if not cfg_file:
            cfg_file = CFGFILE
        config = Config(cfg_file)
        c = []
        for p in config.procs:
            proc = Process(
                name=p.name,
                path=p.path,
                max_nl=p.max_nl,
                bm=self.bm,
                try_restart=-1,
            )
            self.nam_map[proc.name] = proc

    def get_procs(self):
        return self.nam_map.values()

    def start_all(self):
        for proc in self.nam_map.values():
            proc.start()
            self.pid_map[proc.pid] = proc

    def stop_all(self):
        for proc in self.nam_map.values():
            proc.status = STATUS.STOPING
        print os.getpid(), os.getpgrp()
        os.killpg(os.getpgrp(), 15)

    def start(self, procname):
        proc = self.nam_map[procname]
        proc.start()
        # set process group id of the child
        os.setpgid(os.proc.pid, os.getpid())
        self.pid_map[proc.pid] = proc
        return RESULT.SUCCESS

    def stop(self, procname):
        proc = self.nam_map[procname]
        proc.stop()
        return RESULT.SUCCESS

    def restart(self, procname):
        proc = self.nam_map[procname]
        proc.restart()
        return RESULT.SUCCESS

    def status(self, procname):
        if procname == '*':
            pa = []
            for p in self.nam_map.values():
                pa.append(str(p))
            return '\n'.join(pa)
        proc = self.nam_map[procname]
        return str(proc)

    def proc_exit(self, signum, frame):
        pids = []
        while True:
            pid = 0
            try:
                pid, exitcode = os.waitpid(-1, os.WNOHANG | os.WUNTRACED)
            except Exception as e:
                #print 'error:::', e
                pass
            if pid == 0:
                break
            else:
                pids.append(pid)
        for p in self.pid_map.values():
            if p.pid not in pids:
                if not p.proc.is_alive() and p.status == STATUS.RUNNING:
                    pids.append(p.pid)
        for pid in pids:
            proc = self.pid_map.get(pid, None)
            if not proc:
                continue
            proc = proc.cleanup()
            del self.pid_map[pid]
            if proc:
                self.pid_map[proc.pid] = proc

###
### testing
###

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
path = /bin/bash """ + self.daemon_file + """ 0 6 0.07""")
        c.append("""[output proc1]
path = /bin/bash """ + self.daemon_file + """ 1 13 0.2""")
        c.append("""[output proc2]
path = /bin/bash """ + self.daemon_file + """ 2 5 0.3""")
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

    def test_match_procs(self):
        watcher = self.get_watcher()
        assert len(watcher.nam_map.values()) == 3
        for k, v in watcher.nam_map.items():
            assert k.startswith('output proc')
            assert 'READY' in str(v)

    def start_procs(self):
        self.watcher.start_all()
        async.loop()

    def test_start_procs(self):
        self.watcher = self.get_watcher()
        ct_thread = threading.Thread(target=self.stop_ct)
        ct_thread.start()
        self.start_procs()
        ct_thread.join()

    def stop_ct(self):
        time.sleep(2)
        for x in self.watcher.get_procs():
            x.stop()

    def test_restart_procs(self):
        self.watcher = self.get_watcher()
        ct_thread = threading.Thread(target=self.restart_ct)
        ct_thread.start()
        self.start_procs()
        ct_thread.join()

    def restart_ct(self):
        time.sleep(2)
        for x in self.watcher.get_procs():
            x.restart()
        self.stop_ct()

    def blast_module(self, message, index):
        print message.message,
        self.data.append(message.message)
