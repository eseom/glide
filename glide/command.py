import socket
import sys
import optparse


class Result(object):
    SUCCESS = '1'
    FAILURE = '0'


class Command(object):
    def __init__(self, host, command='status', process_name='*'):
        self.host = host
        self.command = command
        self.process_name = process_name

    def send_command(self):
        try:
            sock = socket.create_connection((self.host, 32767))
        except:
            return -1
        try:
            sock.send('%s %s' % (self.command, self.process_name,))
            message = sock.recv(8192)
        except:
            pass
        try:
            sock.close()
            return message
        except:
            pass

    def __call__(self):
        if self.command not in (
           'start', 'restart', 'stop', 'hangup', 'alarm', 'status'):
            command_error(self.command)

        result = self.send_command()

        if result == -1:
            socket_error()

        if self.command == 'status':
            print result
            return

        result_code, message = result.split(' ', 1)
        result_code = bool(int(result_code))
        if result_code:
            message = 'success'
        print 'glide [%s] %s %s' % \
            (self.process_name, self.command, message,)

    def handle_status(cls, result, procname):
        return result


def command_error(command):
    print 'error: no such command: %s' % command
    sys.exit(2)


def socket_error():
    print 'error: cannot connect any running glided process.'
    sys.exit(-1)


def usage():
    print 'usage: glidectl <command> <process name>'
    sys.exit(1)


def main():
    parser = optparse.OptionParser()
    _, argv = parser.parse_args()
    if len(argv) == 0:
        usage()
    if len(argv) < 2:
        if argv[0] == 'status':
            argv.append('*')
        else:
            usage()
    Command('localhost', *argv)()

if __name__ == '__main__':
    main()
