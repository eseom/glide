import asyncore
from glide import logger
from glide.server import CommandServer
from glide.breakhandler import BreakHandler
from glide.watcher import Watcher


class Controller(object):
    def __init__(self):
        self.logger = logger.Log()

    def start(self):
        self.watcher = Watcher(self.logger.info)
        self.watcher.match_procs()
        self.watcher.start_all()
        self.server = \
            CommandServer('0.0.0.0', 32767, self)
        try:
            asyncore.loop()
        except:
            pass

    def stop(self):
        self.server.stop()
        self.watcher.stop_all()

    def __blast_module(self, message, index):
        print index, message.message,

    def command(self, command):
        try:
            command, procname = command.strip().split(' ', 1)
            method = getattr(self.watcher, command)
            if method:
                if command == 'status':
                    return method(procname)
                result, message = method(procname)
                return '%s %s' % (int(result), message,)
        except:
            pass


def main():
    controller = Controller()

    def exit_callback(signal, frame):
        controller.stop()
    bh = BreakHandler()
    bh.register_exit_callback(exit_callback, onlyonce=True)
    controller.start()

if __name__ == '__main__':
    main()
