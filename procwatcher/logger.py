#!/usr/bin/env python
#
# http://github.com/eseom/procwatcher
#
# @author:  EunseokEom <me@eseom.org>
# @desc:    controller

import logging
import logging.handlers

class Log(object):
    def __init__(self):
        self.logger = None

    def get_logger(self):
        try:
            my_logger = logging.getLogger('syslog')
            logging.raiseExceptions = 0
            my_logger.setLevel(logging.DEBUG)
            handler = logging.handlers.SysLogHandler(address = '/dev/log',
                facility=logging.handlers.SysLogHandler.LOG_DAEMON)
            my_logger.addHandler(handler)
            self.logger = my_logger
        except Exception as e:
            pass

    def info(self, message, index):
        if not self.logger:
            self.get_logger()
        if self.logger:
            self.logger.info('%s: %s', message.proc.name, message.message)
