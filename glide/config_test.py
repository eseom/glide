from glide.config import Config
import unittest
import os


class Tester(unittest.TestCase):
    """ prepare test """
    def setUp(self):
        self.cfg_file = 'glide.conf'
        self.remove_config_file()
        c = []
        for i in [1, 2, 3]:
            c.append("""[output proc%s]
path = /usr/local/bin/sample.sh %s""" % (i, i))
        cfg_content = '\n'.join(c)
        with open(self.cfg_file, 'w') as fp:
            fp.write(cfg_content)

    def remove_config_file(self):
        try:
            os.remove(self.cfg_file)
        except:
            pass

    def tearDown(self):
        self.remove_config_file()

    def test_read_config(self):
        config = Config(self.cfg_file)
        procs = config.get_procs()
        self.assertEquals(len(procs), 3)
        for i in [1, 2, 3]:
            self.assertEquals(procs[i - 1].name,
                'output proc' + str(i))
            self.assertEquals(procs[i - 1].path,
                ['/usr/local/bin/sample.sh', str(i)])
            self.assertEquals(procs[i - 1].max_nl,
                len('output proc '))
