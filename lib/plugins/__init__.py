import os
import sys
import yaml

class Plugin(object):
    def __init__(self):
        for cls in reversed(self.__class__.mro()):
            if cls is not object:
                try:
                    cls._init(self)
                except AttributeError as e:
                    pass


    def _init(self):
        module_dir = os.path.dirname(sys.modules[self.__module__].__file__)
        config_file = module_dir + os.sep + 'config.yaml'

        config = {}

        try:
            with open(config_file, 'r') as f:
                self.config = yaml.load(f)
        except FileNotFoundError as e:
            pass


    def run(self, args):
        raise NotImplementedError()

# vim:sw=4:ts=4:et:

