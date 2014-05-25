#!/usr/bin/env python
#
# http://github.com/eseom/procwatcher
#
# @author:  EunseokEom <me@eseom.org>
# @desc:    server handler with the python asyncore module

import asyncore as async
import socket
import unittest
import threading
import functools
import time

PORT = 32767

class CommandBaseHandler(async.dispatcher_with_send):
    def __init__(self, sock):
        async.dispatcher_with_send.__init__(self, sock)

    def handle_read(self):
        data = self.recv(8192)
        if data:
            self.send(self.handle_data(data))

    def handle_data(self):
        raise Exception('<handle_data> not implemented')

class CommandServer(async.dispatcher):
    def __init__(self, host, port, command_handler):
        async.dispatcher.__init__(self)
        self.command_handler = command_handler
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            handler = self.command_handler(sock)

class Tester(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_proc_handler(self):
        client = functools.partial(self.run_client, 'start proc1')
        client_thread = threading.Thread(target=client)
        client_thread.start()
        self.run_server()
        client_thread.join()

    def run_client(self, command):
        time.sleep(1)
        s = socket.create_connection(('localhost', PORT))
        s.send(command)
        data = s.recv(1024)
        s.close()
        async.close_all()
        assert data == command

    def run_server(self):
        server = CommandServer('0.0.0.0', PORT, Tester.EchoCommandHandler)
        async.loop()

    class EchoCommandHandler(CommandBaseHandler):
        def handle_data(self, data):
            return data
