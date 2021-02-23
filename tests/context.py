import os
import sys

from platypush.config import Config

testdir = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(testdir, '..')))
config_file = os.path.join(testdir, 'etc', 'config.yaml')

Config.init(config_file)


class TimeoutException(RuntimeError):
    def __init__(self, msg):
        self.msg = msg


# vim:sw=4:ts=4:et:
