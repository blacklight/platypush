import logging
import os
import socket
import yaml

""" Config singleton instance """
_default_config_instance = None

class Config(object):
    """
    Configuration base class
    Usage:
        - Initialize config from one of the default paths:
            Config.init()
        - Initialize config from a custom path
            Config.init(config_file_path)
        - Set a value
            Config.set('foo', 'bar')
        - Get a value
            Config.get('foo')
    """

    """
    Default config file locations:
        - $HOME/.config/platypush/config.yaml
        - /etc/platypush/config.yaml
    """
    _cfgfile_locations = [
        os.path.join(os.environ['HOME'], '.config', 'platypush', 'config.yaml'),
        os.path.join(os.sep, 'etc', 'platypush', 'config.yaml'),
    ]

    def __init__(self, cfgfile=None):
        """
        Constructor. Always use the class as a singleton (i.e. through
        Config.init), you won't probably need to call the constructor directly
        Params:
            cfgfile -- Config file path (default: retrieve the first
                       available location in _cfgfile_locations)
        """

        if cfgfile is None:
            cfgfile = self._get_default_cfgfile()

        if cfgfile is None:
            raise RuntimeError('No config file specified and nothing found in {}'
                               .format(self._cfgfile_locations))

        with open(cfgfile, 'r') as fp:
            self._config = yaml.load(fp)

        for section in self._config:
            if 'disabled' in self._config[section] \
                    and self._config[section]['disabled']:
                del self._config[section]

        if 'logging' not in self._config:
            self._config['logging'] = logging.INFO
        else:
            self._config['logging'] = getattr(logging, self._config['logging'].upper())

        if 'device_id' not in self._config:
            self._config['device_id'] = socket.gethostname()

        self._init_components()


    def _init_components(self):
        self.backends = {}
        self.plugins = {}
        self.event_hooks = {}

        for key in self._config.keys():
            if key.startswith('backend.'):
                backend_name = '.'.join(key.split('.')[1:])
                self.backends[backend_name] = self._config[key]
            elif key.startswith('event.hook.'):
                hook_name = '.'.join(key.split('.')[2:])
                self.event_hooks[hook_name] = self._config[key]
            else:
                self.plugins[key] = self._config[key]

    @staticmethod
    def get_backends():
        global _default_config_instance
        if _default_config_instance is None: _default_config_instance = Config()
        return _default_config_instance.backends

    @staticmethod
    def get_plugins():
        global _default_config_instance
        if _default_config_instance is None: _default_config_instance = Config()
        return _default_config_instance.plugins

    @staticmethod
    def get_event_hooks():
        global _default_config_instance
        if _default_config_instance is None: _default_config_instance = Config()
        return _default_config_instance.event_hooks

    @staticmethod
    def get_default_pusher_backend():
        """
        Gets the default pusher backend from the config
        """
        backends = [k for k in Config.get_backends().keys()
                    if 'pusher' in Config.get_backends()[k]
                    and Config.get_backends()[k]['pusher'] is True]

        return backends[0] if backends else None


    @classmethod
    def _get_default_cfgfile(cls):
        for location in cls._cfgfile_locations:
            if os.path.isfile(location): return location

    @staticmethod
    def init(cfgfile=None):
        """
        Initializes the config object singleton
        Params:
            cfgfile -- path to the config file - default: _cfgfile_locations
        """
        global _default_config_instance
        _default_config_instance = Config(cfgfile)

    @staticmethod
    def get(key):
        """
        Gets a config value
        Params:
            key -- Config key to get
        """
        global _default_config_instance
        if _default_config_instance is None: _default_config_instance = Config()
        return _default_config_instance._config[key]

    @staticmethod
    def set(key, value):
        """
        Sets a config value
        Params:
            key   -- Config key to set
            value -- Value for key
        """
        global _default_config_instance
        if _default_config_instance is None: _default_config_instance = Config()
        _default_config_instance._config[key] = key

# vim:sw=4:ts=4:et:

