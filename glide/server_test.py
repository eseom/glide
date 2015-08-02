import socket
import unittest
import threading
import functools
import time
import asyncore
from glide.server import CommandServer, CommandBaseHandler

PORT = 32767


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
        time.sleep(1)  # TODO need a blocking queue
        s = socket.create_connection(('localhost', PORT))
        s.send(command)
        data = s.recv(1024)
        s.close()
        asyncore.close_all()
        self.assertEquals(data, command)

    def run_server(self):
        CommandServer(
            '0.0.0.0',
            PORT,
            Tester.Controller(),
            Tester.EchoCommandHandler,
        )
        try:
            asyncore.loop()
        except:
            pass

    class Controller(object):
        def command(self, command):
            return command

    class EchoCommandHandler(CommandBaseHandler):
        def handle_data(self, data):
            assert self.controller.command(data) == data
            return data
