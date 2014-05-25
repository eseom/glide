#!/usr/bin/env python
#
# http://github.com/eseom/procwatcher
#
# @author:  EunseokEom <me@eseom.org>
# @desc:    config parser

import ConfigParser
import unittest
import os
import io

class Process(object):
    def __init__(self, name, path, max_nl):
        self.name =   name
        self.path =   path
        self.max_nl = max_nl

    def __str__(self):
        return '<%s> %s %s' % (self.name, self.path, self.max_nl,)

class Config(object):
    def __init__(self, cfgfile):
        config = ConfigParser.RawConfigParser(allow_no_value=True)
        with open(cfgfile) as fp: config.readfp(io.BytesIO(fp.read()))
        self.procs  = []
        max_nl = 0
        sections = config.sections()
        sections.sort() # sort by key
        for s in sections:
            l = len(s)
            if max_nl < l: max_nl = l
        for s in sections:
            try:
                self.procs.append(Process(
                    name=s,
                    path=config.get(s, 'path').split(' '),
                    max_nl=max_nl
                ))
            except ConfigParser.NoOptionError:
                # TODO logging error in the config file
                pass

    def get_procs(self):
        return self.procs

class Tester(unittest.TestCase):
    """ prepare test """
    def setUp(self):
        self.cfg_file = 'procwatcher.conf'
        c = []
        for i in [1, 2, 3]:
            c.append("""[output proc%s]
path = /bin/bash outputd.sh %s""" % (i, i))
        cfg_content = '\n'.join(c)
        with open(self.cfg_file, 'w') as fp:
            fp.write(cfg_content)

    def tearDown(self):
        os.remove(self.cfg_file)

    def test_read_config(self):
        config = Config(self.cfg_file)
        procs = config.get_procs()
        assert len(procs) == 3
        for i in [1, 2, 3]:
            assert procs[i - 1].name ==   'output proc' + str(i)
            assert procs[i - 1].path ==   ['/bin/bash', 'outputd.sh', str(i)]
            assert procs[i - 1].max_nl == len('output proc ')
