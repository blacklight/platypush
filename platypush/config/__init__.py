import datetime
import logging
import os
import socket
import time
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

    _default_constants = {
        'today': datetime.date.today,
        'now': datetime.datetime.now,
    }

    _workdir_location = os.path.join(os.environ['HOME'], '.local', 'share', 'platypush')

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

        self._cfgfile = cfgfile
        self._config = self._read_config_file(self._cfgfile)

        if 'workdir' not in self._config:
            self._config['workdir'] = self._workdir_location
        os.makedirs(self._config['workdir'], exist_ok=True)

        if 'logging' not in self._config:
            self._config['logging'] = logging.INFO
        else:
            self._config['logging'] = getattr(logging, self._config['logging'].upper())

        if 'device_id' not in self._config:
            self._config['device_id'] = socket.gethostname()

        self.backends = {}
        self.plugins = {}
        self.event_hooks = {}
        self.procedures = {}
        self.constants = {}
        self.cronjobs = {}

        self._init_constants()
        self._init_components()


    def _read_config_file(self, cfgfile):
        if not os.path.isabs(cfgfile):
            cfgfile = os.path.join(os.path.dirname(self._cfgfile), cfgfile)

        config = {}
        with open(cfgfile, 'r') as fp:
            file_config = yaml.load(fp)

        for section in file_config:
            if section == 'include':
                include_files = file_config[section] \
                    if isinstance(file_config[section], list) \
                    else [file_config[section]]

                for include_file in include_files:
                    included_config = self._read_config_file(include_file)
                    for incl_section in included_config.keys():
                        config[incl_section] = included_config[incl_section]
            elif 'disabled' not in file_config[section] \
                    or file_config[section]['disabled'] is False:
                config[section] = file_config[section]

        return config


    def _init_components(self):
        for key in self._config.keys():
            if key.startswith('backend.'):
                backend_name = '.'.join(key.split('.')[1:])
                self.backends[backend_name] = self._config[key]
            elif key.startswith('event.hook.'):
                hook_name = '.'.join(key.split('.')[2:])
                self.event_hooks[hook_name] = self._config[key]
            elif key.startswith('cron.'):
                cron_name = '.'.join(key.split('.')[1:])
                self.cronjobs[cron_name] = self._config[key]
            elif key.startswith('procedure.'):
                tokens = key.split('.')
                async = True if tokens[1] == 'async' else False
                procedure_name = '.'.join(tokens[2:])
                self.procedures[procedure_name] = {
                    'async': async,
                    'actions': self._config[key]
                }
            else:
                self.plugins[key] = self._config[key]

    def _init_constants(self):
        if 'constants' in self._config:
            self.constants = self._config['constants']

        for (key,value) in self._default_constants.items():
            self.constants[key] = value


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
    def get_procedures():
        global _default_config_instance
        if _default_config_instance is None: _default_config_instance = Config()
        return _default_config_instance.procedures

    @staticmethod
    def get_constants():
        global _default_config_instance
        if _default_config_instance is None: _default_config_instance = Config()
        constants = {}

        for name in _default_config_instance.constants.keys():
            constants[name] = Config.get_constant(name)
        return constants

    @staticmethod
    def get_constant(name):
        global _default_config_instance
        if _default_config_instance is None: _default_config_instance = Config()

        if name not in _default_config_instance.constants: return None
        value = _default_config_instance.constants[name]
        return value() if callable(value) else value

    @staticmethod
    def get_cronjobs():
        global _default_config_instance
        if _default_config_instance is None: _default_config_instance = Config()
        return _default_config_instance.cronjobs

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

