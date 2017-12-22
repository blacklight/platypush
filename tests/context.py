import os
import sys

testdir = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(testdir, '..')))
config_file = os.path.join(testdir, 'etc', 'config.yaml')

from platypush.config import Config
Config.init(config_file)

import platypush


class TestTimeoutException(RuntimeError):
    def __init__(self, msg):
        self.msg = msg


# vim:sw=4:ts=4:et:

