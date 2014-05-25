#!/usr/bin/env python
#
# http://github.com/eseom/procwatcher
#
# @author:  EunseokEom <me@eseom.org>
# @desc:    daemonizer

import asyncore as async

from watcher import Watcher

class Daemon(object):
    def __init__(self):
        pass

    def start(self):
        watcher = Watcher(self.__blast_module)
        watcher.match_procs()
        watcher.start_all()
        async.loop()

    def __blast_module(self, message, index):
        print index, message.message,

def main():
    daemon = Daemon()
    daemon.start()

if __name__ == '__main__':
    main()
