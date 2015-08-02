import asyncore
import unittest
import shutil
import os
import signal
import time
import threading
from glide.process import Process


class Tester(unittest.TestCase):
    def setUp(self):
        if not os.path.exists('temp'):
            os.mkdir('temp')
        self.test_file = 'temp/execute.sh'
        test_code = """#!/bin/bash
trap 'for i in $(seq 1 $3); do echo "$1-#"; sleep 0.4; done; exit' SIGTERM
for i in `seq 1 20`; do echo $1-$i; sleep $2; done
"""
        with open(self.test_file, 'w') as fp:
            fp.write(test_code)
        # make executable
        os.chmod(self.test_file, 0777)

        # signal trap
        signal.signal(signal.SIGCHLD, self.proc_exit)

        self.test_blasted = []

    def tearDown(self):
        shutil.rmtree('temp')

    def proc_exit(self, signum, frame):
        pid, exitcode = os.waitpid(-1, os.WNOHANG | os.WUNTRACED)
        self.process.cleanup()

    def blast_save_to_test_blasted(self, message, index):
        self.test_blasted.append('[%s] %s' % (index, message.message,))

    def blast_save_process_to_test_blasted(self, message, index):
        self.test_blasted.append(str(self.process)[0:36])

    def test_normal_execution(self):
        """test output of a normal process"""
        self.process = Process(
            name='test_execute1',
            path=[self.test_file, '1', '0.1', '7'],
            max_nl=10,
            bm=self.blast_save_to_test_blasted,
            try_restart=0,
        )
        result, message = self.process.start()
        self.assertEquals(result, True)
        try:
            asyncore.loop(1)
        except:  # from asyncore.file_dispatcher.close(self)
            pass
        self.assertEquals('\n'.join(self.test_blasted), """[0] 1-1
[1] 1-2
[2] 1-3
[3] 1-4
[4] 1-5
[5] 1-6
[6] 1-7
[7] 1-8
[8] 1-9
[9] 1-10
[10] 1-11
[11] 1-12
[12] 1-13
[13] 1-14
[14] 1-15
[15] 1-16
[16] 1-17
[17] 1-18
[18] 1-19
[19] 1-20""")

    def test_sigterm_execution(self):
        """test output of a terminated process"""
        self.process = Process(
            name='test_execute2',
            path=[self.test_file, '2', '0.3', '7'],
            max_nl=10,
            bm=self.blast_save_to_test_blasted,
            try_restart=0,
        )
        self.process.start()

        def send_signal_to_process():
            """ signal sigterm to the process """
            time.sleep(2)
            self.process.terminate()

        ssp_thread = threading.Thread(target=send_signal_to_process)
        ssp_thread.start()
        try:
            asyncore.loop(1)
        except:  # from asyncore.file_dispatcher.close(self)
            pass
        self.assertEquals('\n'.join(self.test_blasted), """[0] 2-1
[1] 2-2
[2] 2-3
[3] 2-4
[4] 2-5
[5] 2-6
[6] 2-7
[7] 2-#
[8] 2-#
[9] 2-#
[10] 2-#
[11] 2-#
[12] 2-#
[13] 2-#""")

    def test_show_status(self):
        """test showing status of the process"""
        self.process = Process(
            name="text_execute3",
            path=[self.test_file, '3', '0.01', '7'],
            max_nl=20,
            bm=self.blast_save_process_to_test_blasted,
            try_restart=0,
        )
        self.process.start()
        try:
            asyncore.loop(1)
        except:  # from asyncore.file_dispatcher.close(self)
            pass
        self.assertEquals('\n'.join(self.test_blasted), """\
text_execute3           RUNNING  pid
text_execute3           RUNNING  pid
text_execute3           RUNNING  pid
text_execute3           RUNNING  pid
text_execute3           RUNNING  pid
text_execute3           RUNNING  pid
text_execute3           RUNNING  pid
text_execute3           RUNNING  pid
text_execute3           RUNNING  pid
text_execute3           RUNNING  pid
text_execute3           RUNNING  pid
text_execute3           RUNNING  pid
text_execute3           RUNNING  pid
text_execute3           RUNNING  pid
text_execute3           RUNNING  pid
text_execute3           RUNNING  pid
text_execute3           RUNNING  pid
text_execute3           RUNNING  pid
text_execute3           RUNNING  pid
text_execute3           RUNNING  pid""")

    def test_restart(self):
        self.process = Process(
            name="text_execute4",
            path=[self.test_file, '4', '0.2', '7'],
            max_nl=20,
            bm=self.blast_save_to_test_blasted,
            try_restart=0,
        )
        self.process.start()

        def send_signal_to_process():
            """ signal sigterm to the process """
            time.sleep(1)
            self.process.restart()

        ssp_thread = threading.Thread(target=send_signal_to_process)
        ssp_thread.start()
        try:
            asyncore.loop(1)
        except:  # from asyncore.file_dispatcher.close(self)
            pass
        self.assertEquals('\n'.join(self.test_blasted), """\
[0] 4-1
[1] 4-2
[2] 4-3
[3] 4-4
[4] 4-5
[5] 4-#
[6] 4-#
[7] 4-#
[8] 4-#
[9] 4-#
[10] 4-#
[11] 4-#
[12] 4-1
[13] 4-2
[14] 4-3
[15] 4-4
[16] 4-5
[17] 4-6
[18] 4-7
[19] 4-8
[20] 4-9
[21] 4-10
[22] 4-11
[23] 4-12
[24] 4-13
[25] 4-14
[26] 4-15
[27] 4-16
[28] 4-17
[29] 4-18
[30] 4-19
[31] 4-20""")

    def test_hanging_process(self):
        self.process = Process(
            name="text_execute5",
            path=[self.test_file, '5', '0.8', '50'],
            max_nl=20,
            bm=self.blast_save_to_test_blasted,
            try_restart=0,
        )
        self.process.start()

        def send_signal_to_process():
            """ signal sigterm to the process """
            time.sleep(2)
            self.process.terminate()

        ssp_thread = threading.Thread(target=send_signal_to_process)
        ssp_thread.start()
        try:
            asyncore.loop(1)
        except:  # from asyncore.file_dispatcher.close(self)
            pass
        self.assertEquals('\n'.join(self.test_blasted), """\
[0] 5-1
[1] 5-2
[2] 5-3
[3] 5-#
[4] 5-#
[5] 5-#
[6] 5-#
[7] 5-#
[8] 5-#
[9] 5-#
[10] 5-#
[11] 5-#
[12] 5-#
[13] 5-#
[14] 5-#
[15] 5-#
[16] 5-#
[17] 5-#
[18] 5-#
[19] 5-#
[20] 5-#
[21] 5-#
[22] 5-#
[23] 5-#
[24] 5-#
[25] 5-#
[26] 5-#
[27] 5-#
[28] 5-#
[29] 5-#
[30] 5-#
[31] 5-#
[32] 5-#
[33] 5-#
[34] 5-#
[35] 5-#
[36] 5-#
[37] 5-#
[38] 5-#
[39] 5-#
[40] 5-#
[41] 5-#
[42] 5-#
[43] 5-#
[44] 5-#
[45] 5-#
[46] 5-#
[47] 5-#
[48] 5-#
[49] 5-#
[50] 5-#
[51] 5-#
[52] 5-#""")
