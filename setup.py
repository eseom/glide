import os.path, sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from procwatcher.version import VERSION
import multiprocessing # http://bugs.python.org/issue15881#msg170215

def readme():
    with open(os.path.join(os.path.dirname(__file__), 'README.md')) as fp:
        return fp.read()

setup(name='procwatcher',
      packages=['procwatcher'],
      version=VERSION,
      description='simple process management tool',
      long_description=readme(),
      license='MIT License',
      author='EunseokEom',
      author_email='me@eseom.org',
      maintainer='EunseokEom',
      maintainer_email='me@eseom.org',
      test_suite="tests",
      classifiers=[
          'Development Status :: 1 - Pre-Alpha',
          'Environment :: No Input/Output (Daemon)',
          'Intended Audience :: System Administrators',
          'Natural Language :: English',
          'Operating System :: POSIX',
          'Topic :: System :: Boot',
          'Topic :: System :: Monitoring',
          'Topic :: System :: Systems Administration',
      ]
)
