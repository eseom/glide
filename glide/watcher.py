import os
import signal

from glide.config import Config
from glide.process import Process, Status

no_such_process = 'no such process'
default_config_file = '/etc/glide.conf'


class Watcher(object):
    def __init__(self, bm):
        self.bm = bm
        self.nam_map = {}  # key: proc name, value: proc
        self.pid_map = {}  # key: proc pid,  value: proc
        signal.signal(signal.SIGCHLD, self.proc_exit)

    def match_procs(self, cfg_file=default_config_file):
        config = Config(cfg_file)
        for p in config.procs:
            proc = Process(
                name=p.name,
                path=p.path,
                max_nl=p.max_nl,
                bm=self.bm,
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
            proc.status = Status.KLNG
            proc.terminate()

    def start(self, procname):
        proc = self.nam_map.get(procname, None)
        if not proc:
            return False, no_such_process
        result, message = proc.start()
        if result:
            self.pid_map[proc.pid] = proc
        return result, message

    def stop(self, procname):
        proc = self.nam_map.get(procname, None)
        if not proc:
            return False, no_such_process
        return proc.stop()

    def restart(self, procname):
        proc = self.nam_map.get(procname, None)
        if not proc:
            return False, no_such_process
        return proc.restart()

    def hangup(self, procname):
        proc = self.nam_map.get(procname, None)
        if not proc:
            return False, no_such_process
        return proc.hangup()

    def alarm(self, procname):
        proc = self.nam_map.get(procname, None)
        if not proc:
            return False, no_such_process
        return proc.alarm()

    def status(self, procname):
        if procname == '*':
            pa = []
            for p in self.nam_map.values():
                pa.append(str(p))
            return '\n'.join(pa)
        proc = self.nam_map[procname]
        if not proc:
            return False, no_such_process
        return str(proc)

    def proc_exit(self, signum, frame):
        pids = []
        while True:
            pid = 0
            try:
                pid, exitcode = os.waitpid(-1, os.WNOHANG | os.WUNTRACED)
                if exitcode != 0:  # path not exitts
                    p = self.pid_map[pid]
                    p.status = Status.EXTD
                    p.cleanup()
            except Exception:
                pass
            if pid == 0:
                break
            else:
                pids.append(pid)
        for p in self.pid_map.values():
            if p.pid not in pids and \
               not p.process.is_alive() and \
               p.status in (Status.RUNN, Status.KLNG):
                pids.append(p.pid)
        for pid in pids:
            proc = self.pid_map.get(pid, None)
            if not proc:
                continue
            proc = proc.cleanup()
            del self.pid_map[pid]
            if proc:
                self.pid_map[proc.pid] = proc
