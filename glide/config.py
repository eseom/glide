import ConfigParser
import io


class Process(object):
    def __init__(self, name, path, max_nl):
        self.name = name
        self.path = path
        self.max_nl = max_nl

    def __str__(self):
        return '<%s> %s %s' % (self.name, self.path, self.max_nl,)


class Config(object):
    def __init__(self, cfg_file):
        config = ConfigParser.RawConfigParser(allow_no_value=True)
        with open(cfg_file) as fp:
            config.readfp(io.BytesIO(fp.read()))
        self.procs = []
        max_nl = 0
        sections = config.sections()
        sections.sort()  # sort by key
        for s in sections:
            l = len(s)
            if max_nl < l:
                max_nl = l
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
