#!/usr/bin/env python
#
# author: EunseokEom <me@eseom.org>

import logging
import logging.handlers

class Log(object):
    def __init__(self):
        self.logger = None

    def get_logger(self):
        try:
            my_logger = logging.getLogger('MyLogger')
            my_logger.setLevel(logging.DEBUG)
            handler = logging.handlers.SysLogHandler(address = '/dev/log',
                facility=logging.handlers.SysLogHandler.LOG_DAEMON)
            my_logger.addHandler(handler)
            self.logger = my_logger
        except Exception as e:
            pass

    def log(self, procname, message):
        if not self.logger:
            self.get_logger()
        self.logger.info('%s: %s', procname, message)
