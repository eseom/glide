import os
import multiprocessing
import asyncore
import datetime


class Status(object):
    """process status enum"""

    REDY, RUNN, RSTT, STNG, KLNG, STPD, EXTD = \
        'READY', 'RUNNING', 'RESTARTING', \
        'STOPPING', 'KILLING', 'STOPPED', 'EXITED'


class Process(asyncore.file_dispatcher):
    """main process object"""

    class Message(object):
        """container class of the emitted messages from the target process"""
        def __init__(self, process, message):
            self.process = process
            self.message = message

        def __str__(self):
            return '%s: %s' % (self.process.name, self.message)

    def __init__(self,
                 name,
                 path,
                 max_nl,
                 bm,
                 try_restart=-1,
                 kill_duration_time=20,
                 ):
        self.status = Status.REDY  # initial status READY
        self.name = name
        self.path = path
        self.max_nl = max_nl        # max name length
        self.bm = bm                # blast module
        self.try_restart = try_restart
        self.kill_duration_time = kill_duration_time
        self.bi = 0                 # blast index
        self.restarted = 0

        self.rpi = 0
        self.wpi = 0
        self.status = Status.REDY
        self.start_time = None

    def start(self):
        if self.status not in (Status.REDY, Status.STPD, Status.EXTD):
            return False, 'already operating'
        self.rpi, self.wpi = os.pipe()
        self.process = multiprocessing.Process(
            target=self.__execute,
            args=(self.path, self.rpi, self.wpi)
        )
        self.process.start()
        self.pid = self.process.pid

        # register the pipe's reader descriptor to asyncore
        asyncore.file_dispatcher.__init__(self, self.rpi)

        self.status = Status.RUNN
        self.start_time = datetime.datetime.now()
        self.elapsed_rule_time = None
        return True, ''

    def __execute(self, path, rpi, wpi):
        pid = os.getpid()
        # set the child process as a process group master itself
        os.setpgid(pid, pid)
        os.dup2(wpi, 1)
        os.dup2(wpi, 2)
        os.close(wpi)
        os.close(rpi)
        os.execv(path[0], path)

    def handle_read(self):
        data = []
        try:
            while True:  # read data from the pipe's reader
                d = self.recv(1)
                if d == '\n':
                    break
                data.append(d)

            # blast to the registered blast module
            self.bm(Process.Message(self, ''.join(data)), self.bi)
            self.bi += 1
        except OSError:  # tried to read after the descriptor closed
            pass

    def writable(self):
        """trick: add timeout callback implementation"""
        if self.elapsed_rule_time:
            self.elapsed_time = datetime.datetime.now() - self.elapsed_rule_time
            if self.elapsed_time > \
               datetime.timedelta(seconds=self.kill_duration_time):
                os.kill(self.pid, 9)
        return False

    def terminate(self):
        try:
            self.elapsed_rule_time = datetime.datetime.now()
            self.process.terminate()
        except OSError:  # no such process id
            pass

    def stop(self):
        if self.status != Status.RUNN:
            return False, 'not running'
        self.status = Status.STNG
        self.terminate()
        return True, ''

    def restart(self):
        if self.status != Status.RUNN:
            return False, 'not running'
        self.status = Status.RSTT
        self.terminate()
        return True, ''

    def hangup(self):
        if self.status != Status.RUNN:
            return False, 'not running'
        os.kill(self.proc.pid, 1)
        return True, ''

    def alarm(self):
        if self.status != Status.RUNN:
            return False, 'not running'
        os.kill(self.proc.pid, 14)
        return True, ''

    def cleanup(self):
        for descriptor in [self.rpi, self.wpi]:
            try:
                os.close(descriptor)
            except:
                pass
        asyncore.file_dispatcher.close(self)

        if ((self.try_restart == -1 or self.try_restart > self.restarted) and
           self.status == Status.EXTD) or self.status == Status.RSTT:
            self.restarted += 1
            self.status = Status.REDY
            self.start()
            return self
        else:
            self.status = Status.STPD
            return None

    def handle_error(self):
        nil, t, v, tbinfo = asyncore.compact_traceback()
        print '---', nil, t, v, tbinfo

    def __str__(self):
        if self.status not in (Status.STPD, Status.REDY, Status.EXTD):
            tmpl = '%-' + str(self.max_nl) + \
                's %10s  pid %5s, uptime %s sec'
            return tmpl % (self.name,
                           self.status,
                           self.pid,
                           datetime.datetime.now() - self.start_time)
        else:
            tmpl = '%-' + str(self.max_nl) + 's %10s'
            return tmpl % (self.name,
                           self.status,)
