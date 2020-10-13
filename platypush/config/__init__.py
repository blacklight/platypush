import datetime
import importlib
import inspect
import logging
import os
import pathlib
import pkgutil
import re
import socket
import sys
from typing import Optional

import yaml

from platypush.utils import get_hash, is_functional_procedure, is_functional_hook, is_functional_cron

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
        - Get a value
            Config.get('foo')
    """

    """
    Default config file locations:
        - $HOME/.config/platypush/config.yaml
        - /etc/platypush/config.yaml
    """
    _cfgfile_locations = [
        os.path.join(os.path.expanduser('~'), '.config', 'platypush', 'config.yaml'),
        os.path.join(os.sep, 'etc', 'platypush', 'config.yaml'),
    ]

    _default_constants = {
        'today': datetime.date.today,
        'now': datetime.datetime.now,
    }

    _workdir_location = os.path.join(os.path.expanduser('~'), '.local', 'share', 'platypush')
    _included_files = set()

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

        self._cfgfile = os.path.abspath(os.path.expanduser(cfgfile))
        self._config = self._read_config_file(self._cfgfile)

        if 'token' in self._config:
            self._config['token'] = self._config['token']
            self._config['token_hash'] = get_hash(self._config['token'])

        if 'workdir' not in self._config:
            self._config['workdir'] = self._workdir_location
        os.makedirs(self._config['workdir'], exist_ok=True)

        if 'scripts_dir' not in self._config:
            self._config['scripts_dir'] = os.path.join(os.path.dirname(cfgfile), 'scripts')
        os.makedirs(self._config['scripts_dir'], mode=0o755, exist_ok=True)

        init_py = os.path.join(self._config['scripts_dir'], '__init__.py')
        if not os.path.isfile(init_py):
            with open(init_py, 'w') as f:
                f.write('# Auto-generated __init__.py - do not remove\n')

        # Include scripts_dir parent in sys.path so members can be imported in scripts
        # through the `scripts` package
        scripts_parent_dir = str(pathlib.Path(self._config['scripts_dir']).absolute().parent)
        sys.path = [scripts_parent_dir] + sys.path

        self._config['db'] = self._config.get('main.db', {
            'engine': 'sqlite:///' + os.path.join(
                os.path.expanduser('~'), '.local', 'share', 'platypush', 'main.db')
        })

        logging_config = {
            'level': logging.INFO,
            'stream': sys.stdout,
            'format': '%(asctime)-15s|%(levelname)5s|%(name)s|%(message)s',
        }

        if 'logging' in self._config:
            for (k, v) in self._config['logging'].items():
                if k == 'filename':
                    logfile = os.path.expanduser(v)
                    logdir = os.path.dirname(logfile)
                    try:
                        os.makedirs(logdir, exist_ok=True)
                    except Exception as e:
                        print('Unable to create logs directory {}: {}'.format(
                            logdir, str(e)))

                    v = logfile
                    del logging_config['stream']
                elif k == 'level':
                    try:
                        v = int(v)
                    except ValueError:
                        v = getattr(logging, v.upper())

                logging_config[k] = v

        self._config['logging'] = logging_config

        if 'device_id' not in self._config:
            self._config['device_id'] = socket.gethostname()

        if 'environment' in self._config:
            for k, v in self._config['environment'].items():
                os.environ[k] = str(v)

        self.backends = {}
        self.plugins = {}
        self.event_hooks = {}
        self.procedures = {}
        self.constants = {}
        self.cronjobs = {}

        self._init_constants()
        self._load_scripts()
        self._init_components()

    @staticmethod
    def _is_special_token(token):
        return token == 'main.db' or \
               token == 'token' or \
               token == 'token_hash' or \
               token == 'logging' or \
               token == 'workdir' or \
               token == 'device_id' or \
               token == 'environment'

    def _read_config_file(self, cfgfile):
        cfgfile_dir = os.path.dirname(os.path.abspath(
            os.path.expanduser(cfgfile)))

        config = {}

        with open(cfgfile, 'r') as fp:
            file_config = yaml.safe_load(fp)

        if not file_config:
            return config

        for section in file_config:
            if section == 'include':
                include_files = file_config[section] \
                    if isinstance(file_config[section], list) \
                    else [file_config[section]]

                for include_file in include_files:
                    if not os.path.isabs(include_file):
                        include_file = os.path.join(cfgfile_dir, include_file)
                    self._included_files.add(include_file)

                    included_config = self._read_config_file(include_file)
                    for incl_section in included_config.keys():
                        config[incl_section] = included_config[incl_section]
            elif section == 'scripts_dir':
                assert isinstance(file_config[section], str)
                config['scripts_dir'] = os.path.abspath(os.path.expanduser(file_config[section]))
            elif 'disabled' not in file_config[section] \
                    or file_config[section]['disabled'] is False:
                config[section] = file_config[section]

        return config

    def _load_module(self, modname: str, prefix: Optional[str] = None):
        try:
            module = importlib.import_module(modname)
        except Exception as e:
            print('Unhandled exception while importing module {}: {}'.format(modname, str(e)))
            return

        prefix = modname + '.' if prefix is None else prefix
        self.procedures.update(**{
            prefix + name: obj
            for name, obj in inspect.getmembers(module)
            if is_functional_procedure(obj)
        })

        self.event_hooks.update(**{
            prefix + name: obj
            for name, obj in inspect.getmembers(module)
            if is_functional_hook(obj)
        })

        self.cronjobs.update(**{
            prefix + name: obj
            for name, obj in inspect.getmembers(module)
            if is_functional_cron(obj)
        })

    def _load_scripts(self):
        scripts_dir = self._config['scripts_dir']
        sys_path = sys.path.copy()
        sys.path = [scripts_dir] + sys.path
        scripts_modname = os.path.basename(scripts_dir)
        self._load_module(scripts_modname, prefix='')

        for _, modname, _ in pkgutil.walk_packages(path=[scripts_dir], onerror=lambda x: None):
            self._load_module(modname)

        sys.path = sys_path

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
                _async = True if len(tokens) > 2 and tokens[1] == 'async' else False
                procedure_name = '.'.join(tokens[2:] if len(tokens) > 2 else tokens[1:])
                args = []
                m = re.match(r'^([^(]+)\(([^)]+)\)\s*', procedure_name)

                if m:
                    procedure_name = m.group(1).strip()
                    args = [
                        arg.strip()
                        for arg in m.group(2).strip().split(',')
                        if arg.strip()
                    ]

                self.procedures[procedure_name] = {
                    '_async': _async,
                    'actions': self._config[key],
                    'args': args,
                }
            elif not self._is_special_token(key):
                self.plugins[key] = self._config[key]

    def _init_constants(self):
        if 'constants' in self._config:
            self.constants = self._config['constants']

        for (key, value) in self._default_constants.items():
            self.constants[key] = value

    @staticmethod
    def get_backends():
        global _default_config_instance
        if _default_config_instance is None:
            _default_config_instance = Config()
        return _default_config_instance.backends

    @staticmethod
    def get_plugins():
        global _default_config_instance
        if _default_config_instance is None:
            _default_config_instance = Config()
        return _default_config_instance.plugins

    @staticmethod
    def get_event_hooks():
        global _default_config_instance
        if _default_config_instance is None:
            _default_config_instance = Config()
        return _default_config_instance.event_hooks

    @staticmethod
    def get_procedures():
        global _default_config_instance
        if _default_config_instance is None:
            _default_config_instance = Config()
        return _default_config_instance.procedures

    @staticmethod
    def get_constants():
        global _default_config_instance
        if _default_config_instance is None:
            _default_config_instance = Config()
        constants = {}

        for name in _default_config_instance.constants.keys():
            constants[name] = Config.get_constant(name)
        return constants

    @staticmethod
    def get_constant(name):
        global _default_config_instance
        if _default_config_instance is None:
            _default_config_instance = Config()

        if name not in _default_config_instance.constants:
            return None
        value = _default_config_instance.constants[name]
        return value() if callable(value) else value

    @staticmethod
    def get_cronjobs():
        global _default_config_instance
        if _default_config_instance is None:
            _default_config_instance = Config()
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
            if os.path.isfile(location):
                return location

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
    def get(key: Optional[str] = None):
        """
        Get a config value or the whole configuration object.

        :param key: Configuration entry to get (default: all entries).
        """
        global _default_config_instance
        if _default_config_instance is None:
            _default_config_instance = Config()

        if key:
            return _default_config_instance._config.get(key)

        return _default_config_instance._config

# vim:sw=4:ts=4:et:
