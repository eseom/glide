#!/usr/bin/env python
#
# http://github.com/eseom/procwatcher
#
# @author:  EunseokEom <me@eseom.org>
# @desc:    controller

import asyncore as async

from watcher import Watcher
import logger
import server
from BreakHandler import BreakHandler

class CommandHandler(server.CommandBaseHandler):
    def handle_data(self, data):
        return self.controller.command(data)

class Controller(object):
    def __init__(self):
        self.logger = logger.Log()

    def start(self):
        self.watcher = Watcher(self.logger.info)
        self.watcher.match_procs()
        self.watcher.start_all()

        self.server = \
            server.CommandServer('0.0.0.0', 32767, self, CommandHandler)
        async.loop()

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
                return method(procname)
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
