import sys, time, signal, os

class BreakHandler(object):
    def __init__(self):
        self.exited = False

    def handle_signal(self, callback):
        for i in [x for x in dir(signal) if x.startswith("SIG")]:
            try:
                signum = getattr(signal, i)
                if signum not in (13, 17, 28):
                    signal.signal(signum, callback)
            except RuntimeError as e:
                pass
            except ValueError as e:
                pass

    def register_exit_callback(self, _callback, onlyonce=False, cascade=False):
        def callback(signal, frame):
            if onlyonce and self.exited:
                return
            if cascade:
                if os.getpgrp() == os.getpid():
                    os.killpg(os.getpgrp(), signal)
            if onlyonce:
                self.exited = True
            _callback(signal, frame)
        self.handle_signal(callback)
