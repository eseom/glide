#!/usr/bin/env python
#
# http://github.com/eseom/procwatcher
#
# @author:  EunseokEom <me@eseom.org>
# @desc:    process handler with the python asyncore module

from multiprocessing import Process as Proc

import asyncore as async
import signal
import unittest
import os
import time
import datetime
import fcntl

class STATUS(object):
    """
    enum class
    """
    READY   = 'READY'
    RUNNING = 'RUNNING'
    RSTTING = 'RESTARTING'
    STOPING = 'STOPPING'
    HANGING = 'HANGINGUP'
    STOPPED = 'STOPPED'

class Message(object):
    def __init__(self, proc, message):
        self.proc = proc
        self.message = message

    def __str__(self):
        return '%s: %s' % (str(self.proc), self.message,)

class FileDispatcher(async.file_dispatcher):
    def __init__(self):
        async.dispatcher.__init__(self)

    def add_channel(self, fd):
        flags = fcntl.fcntl(fd, fcntl.F_GETFL, 0)
        flags = flags | os.O_NONBLOCK
        fcntl.fcntl(fd, fcntl.F_SETFL, flags)
        try:
            # close already opened connection, lazy close
            self.socket.close()
        except:
            pass
        self.socket = async.file_wrapper(fd)
        self._fileno = self.socket.fileno()
        async.file_dispatcher.add_channel(self)

class Process(FileDispatcher):
    """
    invoke one process
    """
    def __init__(self, name, path, max_nl, bm, try_restart=-1):
        self.status      = STATUS.READY
        self.start_time  = None
        self.try_restart = try_restart
        self.parent      = FileDispatcher
        self.restarted   = 0
        self.bi          = 0
        self.name        = name
        self.path        = path
        self.max_nl      = max_nl
        self.bm          = bm
        self.parent.__init__(self)

    def start(self):
        if self.status not in (STATUS.STOPPED, STATUS.READY):
            print 'not stopped'
            return False
        self.rpi, self.wpi = os.pipe()
        self.proc = Proc(
            target=self.__execute,
            args=(self.path, self.rpi, self.wpi)
        )
        self.proc.start()
        self.pid = self.proc.pid
        self.add_channel(self.rpi)
        self.status = STATUS.RUNNING
        self.start_time = datetime.datetime.now()

    def __execute(self, path, rpi, wpi):
        os.dup2(wpi, 1)
        os.dup2(wpi, 2)
        os.close(wpi)
        os.close(rpi)
        os.execv(path[0], path)

    def handle_read(self):
        data = self.recv(4096)
        self.bm(Message(self, data), self.bi)
        self.bi += 1

    def terminate(self):
        self.proc.terminate()

    def stop(self):
        if self.status != STATUS.RUNNING:
            print 'not running'
            return False
        self.proc.terminate()
        self.status = STATUS.STOPING

    def cleanup(self):
        if self.status == STATUS.RUNNING:
            self.status = STATUS.RSTTING
        os.close(self.rpi)
        os.close(self.wpi)
        self.del_channel()
        if (self.try_restart == -1 or \
            self.try_restart > self.restarted) and \
            self.status == STATUS.RSTTING:
            self.restarted += 1
            self.status = STATUS.READY
            self.start()
            return self
        else:
            self.close()
            self.status = STATUS.STOPPED
            return None

    def __str__(self):
        uptime, pid = \
            0, None
        if self.status not in (STATUS.STOPPED, STATUS.READY):
            _uptime = (datetime.datetime.now() - self.start_time)
            uptime  = int(_uptime.total_seconds())
            pid = self.pid
            tmpl = '%-' + str(self.max_nl) + \
                's %10s  pid %5s, uptime %s sec'
            return tmpl % (self.name, self.status, pid, uptime,)
        else:
            tmpl = '%-' + str(self.max_nl) + 's %10s'
            return tmpl % (self.name, self.status,)

    def test_blast(self, data, index):
        print 'internal', data

###
### testing
###

class Tester(unittest.TestCase):
    """ prepare test """
    def setUp(self):
        self.test_file = 'echo.sh' + str(time.time())
        self.terminate_sign_num = 7
        test_code = """#!/bin/bash
trap 'for i in `seq 1 """ + str(self.terminate_sign_num) + \
"""`; do echo -n "$1-#"; sleep $2; done; exit' SIGTERM
for i in `seq 1 20`; do echo -n $1-$i; sleep $2; done
"""
        with open(self.test_file, 'w') as fp:
            fp.write(test_code)
        os.chmod(self.test_file, 0777)

        self.pid_map = {}
        signal.signal(signal.SIGCHLD, self.proc_exit)

    def tearDown(self):
        try:
            os.remove(self.test_file)
        except:
            pass

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
        #for p in self.pid_map.values():
        #    if p.pid not in pids:
        #        print p.proc.is_alive()
        #        if not p.proc.is_alive():
        #            pids.append(p.pid)
        for pid in pids:
            proc = self.pid_map[pid].cleanup()
            del self.pid_map[pid]
            if proc:
                self.pid_map[proc.pid] = proc

    def close_all(self):
        for x in async.socket_map.values():
            x.stop()

    def blast(self, message, index):
        procnum, data =  message.message.split('-')
        self.data[procnum].append(data)
        #print '------', message.proc.restarted,
        #print data,
        #print index
        if index == 43:
            for p in self.pid_map.values():
                p.stop()

    def test_stop_proc_handler(self):
        for sleep in ['0.05', '0.08']:
        #for sleep in ['0.15']:
            self.data = {
                '1': [],
                '2': [],
            }
            for i in self.data.keys():
                proc = Process(
                    name='test_daemon',
                    path=[self.test_file, i, sleep],
                    max_nl=11,
                    bm=self.blast,
                    try_restart=6
                )
                proc.start()
                self.pid_map[proc.pid] = proc
            try:
                async.loop()
            except:
                self.tearDown()
            for i in self.data.keys():
                pos = len(self.data[i]) - self.terminate_sign_num
                assert self.data[i][pos:] == \
                    ['#'] * self.terminate_sign_num
