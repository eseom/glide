import asyncore
import socket


class CommandHandler(asyncore.dispatcher_with_send):
    def __init__(self, commander, sock):
        self.commander = commander
        asyncore.dispatcher_with_send.__init__(self, sock)

    def handle_read(self):
        data = self.recv(8192)
        if data:
            self.sendall(self.commander.command(data))


class CommandServer(asyncore.dispatcher):
    def __init__(self, host, port, commander):
        """
        commander:
            an intsnace of class that has "command(self, command)" interface
        """
        assert hasattr(commander, 'command')

        asyncore.dispatcher.__init__(self)
        self.commander = commander
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def stop(self):
        self.close()

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            # instanciate the subclass of asyncore.dispatcher_with_send.__init__
            CommandHandler(self.commander, sock)
