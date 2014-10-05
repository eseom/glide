#!/usr/bin/env python
#
# http://github.com/eseom/procwatcher
#
# @author:  EunseokEom <me@eseom.org>
# @desc:    logger

import logging
import logging.handlers
from socket import error as socket_error

class Log(object):
    def __init__(self):
        self.logger = None
        self.queue = []
        self.get_logger()

    def handle_error(self, record):
        self.logger.removeHandler(self.handler)
        self.logger = None

    def get_logger(self):
        self.logger = logging.getLogger('syslog')
        self.logger.setLevel(logging.DEBUG)
        try:
            self.handler = logging.handlers.SysLogHandler(address='/dev/log',
                facility=logging.handlers.SysLogHandler.LOG_DAEMON)
            self.handler.handleError = self.handle_error
            self.logger.addHandler(self.handler)
        except socket_error as e:
            self.logger.removeHandler(self.handler)
            self.logger = None

    def info(self, message, index):
        if not self.logger:
            self.get_logger()
        if not self.logger:
            return
        try:
            self.logger.info('%s: %s', message.proc.name, message.message)
        except Exception as e:
            pass
