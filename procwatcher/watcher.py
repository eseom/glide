#!/usr/bin/env python
#
# author: EunseokEom <me@eseom.org>

import io
import os
import datetime
import select
import socket
import signal
import fcntl
import ConfigParser

from multiprocessing import Process

from command import RESULT

PORT = 32767
CFGFILE = '/etc/procwatcher.conf'

def set_nonblock(fd):
    try:
        fd = fd.fileno()
    except AttributeError:
        pass
    flags = fcntl.fcntl(fd, fcntl.F_GETFL, 0)
    flags = flags | os.O_NONBLOCK
    fcntl.fcntl(fd, fcntl.F_SETFL, flags)

def prepare_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    set_nonblock(s)
    s.bind(('0.0.0.0', PORT))
    s.listen(1)
    return s

class STATUS(object):
    RUNNING = 'RUNNING'
    RSTTING = 'RESTARTING'
    STOPING = 'STOPPING'
    HANGING = 'HANGINGUP'
    STOPPED = 'STOPPED'

class Message(object):
    def __init__(self, procname, message):
        self.procname = procname
        self.message = message

    def __str__(self):
        return '%s: %s' % (self.procname, self.message,)

class Proc(object):
    def __init__(self, name, path, max_nl):
        self.name   = name
        self.path   = path
        self.max_nl = max_nl

        self.status = STATUS.STOPPED
        self.start_time = None

    def join(self):
        self.process.join()

    def __str__(self):
        uptime, pid = \
            0, None
        if self.status != STATUS.STOPPED:
            _uptime = (datetime.datetime.now() - self.start_time)
            uptime  = int(_uptime.total_seconds())
            pid = self.pid
            tmpl = '%-' + str(self.max_nl) + \
                's %10s  pid %5s, uptime %s sec'
            return tmpl % (self.name, self.status, pid, uptime,)
        else:
            tmpl = '%-' + str(self.max_nl) + 's %10s'
            return tmpl % (self.name, self.status,)

    @classmethod
    def get_procs(cls, cfgfile):
        config = ConfigParser.RawConfigParser(allow_no_value=True)
        with open(cfgfile) as fp: config.readfp(io.BytesIO(fp.read()))
        procs  = {}
        max_nl = 0
        sections = config.sections()
        sections.sort()
        for s in sections:
            l = len(s)
            if max_nl < l: max_nl = l
        for s in sections:
            try:
                procs[s] = cls(name=s,
                               path=config.get(s, 'path').split(' '),
                               max_nl=max_nl)
            except ConfigParser.NoOptionError:
                # TODO logging error in the config file
                pass
        return procs

class Watcher(object):
    pids  = {}
    rpis  = {}
    procs = {}

    def get_rpis(self):
        return self.rpis.keys() # deep copy

    def command(self, command):
        try:
            command, procname = command.strip().split(' ', 1)
            if command == 'start':
                proc = self.procs[procname]
                return getattr(self, command)(procname, proc)
            else:
                return getattr(self, command)(procname)
        except Exception as e:
            return RESULT.FAIL

    def status(self, name):
        result = []
        if name == '*':
            for proc in self.procs.values():
                result.append(str(proc))
        else:
            result.append(str(self.procs[name]))
        return '\n'.join(result)

    def start(self, name, proc):
        if proc.status != STATUS.STOPPED:
            return RESULT.FAIL
        rpi, wpi = os.pipe()
        signal.signal(signal.SIGCHLD, self.proc_exit);
        process = Process(
            target=self.__execute,
            args=(proc.path, rpi, wpi),
        )
        process.start()
        proc.process = process
        proc.pid = process.pid
        proc.status = STATUS.RUNNING
        proc.start_time = datetime.datetime.now()
        self.pids[process.pid] = (rpi, wpi, proc,)
        self.procs[name] = proc
        self.rpis[rpi] = proc
        return RESULT.SUCCESS

    def stop(self, name):
        proc = self.procs[name]
        if proc.status != STATUS.RUNNING:
            return RESULT.FAIL
        os.kill(proc.pid, 15)
        proc.status = STATUS.STOPING
        return RESULT.SUCCESS

    def hangup(self, name):
        proc = self.procs[name]
        if proc.status != STATUS.RUNNING:
            return RESULT.FAIL
        os.kill(proc.pid, 1)
        proc.status = STATUS.HANGING
        return RESULT.SUCCESS

    def alarm(self, name):
        proc = self.procs[name]
        if proc.status != STATUS.RUNNING:
            return RESULT.FAIL
        os.kill(proc.pid, 14)
        return RESULT.SUCCESS

    def restart(self, name):
        proc = self.procs[name]
        if proc.status != STATUS.RUNNING:
            return RESULT.FAIL
        os.kill(proc.pid, 15)
        proc.status = STATUS.RSTTING
        return RESULT.SUCCESS

    def __execute(self, path, rpi, wpi):
        os.dup2(wpi, 1)
        os.dup2(wpi, 2)
        os.close(wpi)
        os.close(rpi)
        os.execv(path[0], path)

    def proc_exit(self, signum, frame):
        pids = []
        while True:
            pid = 0
            try:    pid, exitcode = os.waitpid(-1, os.WNOHANG | os.WUNTRACED)
            except: pass
            if pid == 0:
                break
            pids.append(pid)
        for p in self.procs.values():
            if p.pid not in pids:
                if not p.process.is_alive():
                    pids.append(p.pid)
        for pid in pids:
            try:
                rpi, wpi, proc = self.pids[pid]
                del self.rpis[rpi]
                del self.pids[pid]
                os.close(wpi)
                os.close(rpi)
                if proc.status == STATUS.STOPING:
                    proc.status = STATUS.STOPPED
                else:
                    proc.status = STATUS.STOPPED
                    self.start(proc.name, proc)
            except: pass

class Daemon(object):
    def __init__(self, cfgfile, message_callback=None):
        self.cfgfile = cfgfile
        self.message_callback = message_callback
        self.running = False

    def start(self):
        watcher = Watcher()
        try:
            ps = Proc.get_procs(self.cfgfile)
        except IOError as e:
            print e
            return
        for k in ps.keys():
            watcher.start(k, ps[k])
        server  = prepare_socket()
        clients = []
        j = 0
        server_rflist  = [server]
        self.running = True
        while True:
            rflist = watcher.get_rpis()
            rflist += server_rflist
            try:
                io, oo, eo = select.select(rflist, [], [], 0.5)
            except select.error as e:
                pass
            j += 1
            for i in io:
                if i == server:
                    try:
                        client, address = server.accept()
                        set_nonblock(client)
                        server_rflist.append(client)
                        clients.append(client)
                    except: pass
                elif i in clients:
                    try:
                        command = i.recv(1024).strip()
                        if command:
                            if command == 'quit procwatcher':
                                self.running = False
                                for p in ps.values():
                                    watcher.stop(p.name)
                                i.send(RESULT.SUCCESS)
                            if self.running:
                                i.send(watcher.command(command))
                        else:
                            try:    i.close()
                            except: pass
                            server_rflist.remove(i)
                            clients.remove(i)
                    except Exception as e: # TODO inspect exception
                        # socket.error
                        try:    i.close()
                        except: pass
                        server_rflist.remove(i)
                        clients.remove(i)
                else:
                    try:
                        data = os.read(i, 1024).strip()
                        for d in data.split('\n'):
                            self.message_callback(
                                Message(watcher.rpis[i].name, d))
                    except: pass
            if not self.running:
                if not watcher.rpis:
                    break
        for p in ps.values():
            p.join()

def main():
    def callback(message):
        print message
        if message.procname not in returned_data.keys():
            returned_data[message.procname] = []
        #returned_data[message.procname].append(message.message)
    daemon = Daemon(CFGFILE, message_callback=callback)
    daemon.start()

if __name__ == '__main__':
    main()
