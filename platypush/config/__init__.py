import datetime
import glob
import importlib
import inspect
import logging
import os
import pathlib
import pkgutil
import re
import shutil
import socket
import sys
from urllib.parse import quote
from typing import Dict, Optional, Set

import yaml

from platypush.utils import (
    get_hash,
    is_functional_procedure,
    is_functional_hook,
    is_functional_cron,
)


class Config:
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

    # Default config file locations:
    #   - current directory
    #   - $HOME/.config/platypush/config.yaml
    #   - /etc/platypush/config.yaml
    _cfgfile_locations = [
        os.path.join(os.path.abspath('.'), 'config.yaml'),
        os.path.join(os.path.expanduser('~'), '.config', 'platypush', 'config.yaml'),
        os.path.join(os.sep, 'etc', 'platypush', 'config.yaml'),
    ]

    # Config singleton instance
    _instance = None

    _default_constants = {
        'today': datetime.date.today,
        'now': datetime.datetime.now,
    }

    _workdir_location = os.path.join(
        os.path.expanduser('~'), '.local', 'share', 'platypush'
    )
    _included_files: Set[str] = set()

    def __init__(self, cfgfile: Optional[str] = None):
        """
        Constructor. Always use the class as a singleton (i.e. through
        Config.init), you won't probably need to call the constructor directly

        :param cfgfile: Config file path (default: retrieve the first available
            location in _cfgfile_locations).
        """

        self.backends = {}
        self.plugins = self._core_plugins
        self.event_hooks = {}
        self.procedures = {}
        self.constants = {}
        self.cronjobs = {}
        self.dashboards = {}
        self._plugin_manifests = {}
        self._backend_manifests = {}
        self._cfgfile = ''

        self._init_cfgfile(cfgfile)
        self._config = self._read_config_file(self._cfgfile)

        self._init_secrets()
        self._init_dirs()
        self._init_db()
        self._init_logging()
        self._init_device_id()
        self._init_environment()
        self._init_manifests()
        self._init_constants()
        self._load_scripts()
        self._init_components()
        self._init_dashboards(self._config['dashboards_dir'])

    def _init_cfgfile(self, cfgfile: Optional[str] = None):
        if cfgfile is None:
            cfgfile = self._get_default_cfgfile()

        if cfgfile is None:
            cfgfile = self._create_default_config()

        self._cfgfile = os.path.abspath(os.path.expanduser(cfgfile))

    def _init_logging(self):
        logging_config = {
            'level': logging.INFO,
            'stream': sys.stdout,
            'format': '%(asctime)-15s|%(levelname)5s|%(name)s|%(message)s',
        }

        if 'logging' in self._config:
            for k, v in self._config['logging'].items():
                if k == 'filename':
                    logfile = os.path.expanduser(v)
                    logdir = os.path.dirname(logfile)
                    try:
                        os.makedirs(logdir, exist_ok=True)
                    except Exception as e:
                        print(f'Unable to create logs directory {logdir}: {e}')

                    v = logfile
                    del logging_config['stream']
                elif k == 'level':
                    try:
                        v = int(v)
                    except ValueError:
                        v = getattr(logging, v.upper())

                logging_config[k] = v

        self._config['logging'] = logging_config

    def _init_db(self):
        # Initialize the default db connection string
        db_engine = self._config.get('main.db', '')
        if db_engine:
            if isinstance(db_engine, str):
                db_engine = {
                    'engine': db_engine,
                }
        else:
            db_engine = {
                'engine': 'sqlite:///'
                + os.path.join(quote(self._config['workdir']), 'main.db')
            }

        self._config['db'] = db_engine

    def _init_device_id(self):
        if 'device_id' not in self._config:
            self._config['device_id'] = socket.gethostname()

    def _init_environment(self):
        if 'environment' in self._config:
            for k, v in self._config['environment'].items():
                os.environ[k] = str(v)

    def _init_dirs(self):
        if 'workdir' not in self._config:
            self._config['workdir'] = self._workdir_location
        self._config['workdir'] = os.path.expanduser(self._config['workdir'])
        os.makedirs(self._config['workdir'], exist_ok=True)

        if 'scripts_dir' not in self._config:
            self._config['scripts_dir'] = os.path.join(
                os.path.dirname(self._cfgfile), 'scripts'
            )
        os.makedirs(self._config['scripts_dir'], mode=0o755, exist_ok=True)

        if 'dashboards_dir' not in self._config:
            self._config['dashboards_dir'] = os.path.join(
                os.path.dirname(self._cfgfile), 'dashboards'
            )
        os.makedirs(self._config['dashboards_dir'], mode=0o755, exist_ok=True)

        # Create a default (empty) __init__.py in the scripts folder
        init_py = os.path.join(self._config['scripts_dir'], '__init__.py')
        if not os.path.isfile(init_py):
            with open(init_py, 'w') as f:
                f.write('# Auto-generated __init__.py - do not remove\n')

        # Include scripts_dir parent in sys.path so members can be imported in scripts
        # through the `scripts` package
        scripts_parent_dir = str(
            pathlib.Path(self._config['scripts_dir']).absolute().parent
        )
        sys.path = [scripts_parent_dir] + sys.path

    def _init_secrets(self):
        if 'token' in self._config:
            self._config['token_hash'] = get_hash(self._config['token'])

    @property
    def _core_plugins(self) -> Dict[str, dict]:
        return {
            'variable': {},
        }

    def _create_default_config(self):
        cfg_mod_dir = os.path.dirname(os.path.abspath(__file__))
        cfgfile = self._cfgfile_locations[0]
        cfgdir = pathlib.Path(cfgfile).parent
        cfgdir.mkdir(parents=True, exist_ok=True)
        for cfgfile in glob.glob(os.path.join(cfg_mod_dir, 'config*.yaml')):
            shutil.copy(cfgfile, str(cfgdir))

        return cfgfile

    def _read_config_file(self, cfgfile):
        cfgfile_dir = os.path.dirname(os.path.abspath(os.path.expanduser(cfgfile)))

        config = {}

        with open(cfgfile, 'r') as fp:
            file_config = yaml.safe_load(fp)

        if not file_config:
            return config

        for section in file_config:
            if section == 'include':
                include_files = (
                    file_config[section]
                    if isinstance(file_config[section], list)
                    else [file_config[section]]
                )

                for include_file in include_files:
                    if not include_file:
                        continue
                    if not os.path.isabs(include_file):
                        include_file = os.path.join(cfgfile_dir, include_file)

                    self._included_files.add(include_file)
                    config.update(self._read_config_file(include_file))
            elif section == 'scripts_dir':
                assert isinstance(file_config[section], str)
                config['scripts_dir'] = os.path.abspath(
                    os.path.expanduser(file_config[section])
                )
            else:
                section_config = file_config.get(section, {}) or {}
                if not (
                    hasattr(section_config, 'get') and section_config.get('disabled')
                ):
                    config[section] = section_config

        return config

    def _load_module(self, modname: str, prefix: Optional[str] = None):
        try:
            module = importlib.import_module(modname)
        except Exception as e:
            print(f'Unhandled exception while importing module {modname}: {e}')
            return

        prefix = modname + '.' if prefix is None else prefix
        self.procedures.update(
            **{
                prefix + name: obj
                for name, obj in inspect.getmembers(module)
                if is_functional_procedure(obj)
            }
        )

        self.event_hooks.update(
            **{
                prefix + name: obj
                for name, obj in inspect.getmembers(module)
                if is_functional_hook(obj)
            }
        )

        self.cronjobs.update(
            **{
                prefix + name: obj
                for name, obj in inspect.getmembers(module)
                if is_functional_cron(obj)
            }
        )

    def _load_scripts(self):
        scripts_dir = self._config['scripts_dir']
        sys_path = sys.path.copy()
        sys.path = [scripts_dir] + sys.path
        scripts_modname = os.path.basename(scripts_dir)
        self._load_module(scripts_modname, prefix='')

        for _, modname, _ in pkgutil.walk_packages(
            path=[scripts_dir], onerror=lambda _: None
        ):
            self._load_module(modname)

        sys.path = sys_path

    def _init_components(self):
        for key, component in self._config.items():
            if (
                key.startswith('backend.')
                and '.'.join(key.split('.')[1:]) in self._backend_manifests
            ):
                backend_name = '.'.join(key.split('.')[1:])
                self.backends[backend_name] = component
            elif key.startswith('event.hook.'):
                hook_name = '.'.join(key.split('.')[2:])
                self.event_hooks[hook_name] = component
            elif key.startswith('cron.'):
                cron_name = '.'.join(key.split('.')[1:])
                self.cronjobs[cron_name] = component
            elif key.startswith('procedure.'):
                tokens = key.split('.')
                _async = bool(len(tokens) > 2 and tokens[1] == 'async')
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
                    'actions': component,
                    'args': args,
                }
            elif key in self._plugin_manifests:
                self.plugins[key] = component

    def _init_manifests(self, base_dir: Optional[str] = None):
        if not base_dir:
            base_dir = os.path.abspath(os.path.join(__file__, '..', '..'))
            plugins_dir = os.path.join(base_dir, 'plugins')
            backends_dir = os.path.join(base_dir, 'backend')
            self._init_manifests(plugins_dir)
            self._init_manifests(backends_dir)
        else:
            manifests_map = (
                self._plugin_manifests
                if base_dir.endswith('plugins')
                else self._backend_manifests
            )
            for mf in pathlib.Path(base_dir).rglob('manifest.yaml'):
                with open(mf, 'r') as f:
                    manifest = yaml.safe_load(f)['manifest']
                    comp_name = '.'.join(manifest['package'].split('.')[2:])
                    manifests_map[comp_name] = manifest

    def _init_constants(self):
        if 'constants' in self._config:
            self.constants = self._config['constants']

        for key, value in self._default_constants.items():
            self.constants[key] = value

    def _get_dashboard(
        self, name: str, dashboards_dir: Optional[str] = None
    ) -> Optional[str]:
        dashboards_dir = dashboards_dir or self._config['dashboards_dir']
        assert dashboards_dir
        abspath = os.path.join(dashboards_dir, name + '.xml')
        if not os.path.isfile(abspath):
            return None

        with open(abspath, 'r') as fp:
            return fp.read()

    def _get_dashboards(self, dashboards_dir: Optional[str] = None) -> dict:
        dashboards = {}
        dashboards_dir = dashboards_dir or self._config['dashboards_dir']
        assert dashboards_dir

        for f in os.listdir(dashboards_dir):
            abspath = os.path.join(dashboards_dir, f)
            if not os.path.isfile(abspath) or not abspath.endswith('.xml'):
                continue

            name = f.split('.xml')[0]
            dashboards[name] = self._get_dashboard(name, dashboards_dir)

        return dashboards

    @classmethod
    def _get_instance(
        cls, cfgfile: Optional[str] = None, force_reload: bool = False
    ) -> "Config":
        """
        Lazy getter/setter for the default configuration instance.
        """
        if force_reload or cls._instance is None:
            cfg_args = [cfgfile] if cfgfile else []
            cls._instance = Config(*cfg_args)
        return cls._instance

    @classmethod
    def get_dashboard(
        cls, name: str, dashboards_dir: Optional[str] = None
    ) -> Optional[str]:
        # pylint: disable=protected-access
        return cls._get_instance()._get_dashboard(name, dashboards_dir)

    @classmethod
    def get_dashboards(cls, dashboards_dir: Optional[str] = None) -> dict:
        # pylint: disable=protected-access
        return cls._get_instance()._get_dashboards(dashboards_dir)

    def _init_dashboards(self, dashboards_dir: str):
        self.dashboards = self._get_dashboards(dashboards_dir)

    @classmethod
    def get_backends(cls):
        return cls._get_instance().backends

    @classmethod
    def get_plugins(cls):
        return cls._get_instance().plugins

    @classmethod
    def get_event_hooks(cls):
        return cls._get_instance().event_hooks

    @classmethod
    def get_procedures(cls):
        return cls._get_instance().procedures

    @classmethod
    def get_constants(cls):
        return {
            name: Config.get_constant(name) for name in cls._get_instance().constants
        }

    @classmethod
    def get_constant(cls, name):
        value = cls._get_instance().constants.get(name)
        if value is None:
            return None
        return value() if callable(value) else value

    @classmethod
    def get_cronjobs(cls):
        return cls._get_instance().cronjobs

    @classmethod
    def _get_default_cfgfile(cls) -> Optional[str]:
        for location in cls._cfgfile_locations:
            if os.path.isfile(location):
                return location
        return None

    @classmethod
    def init(cls, cfgfile: Optional[str] = None):
        """
        Initializes the config object singleton
        Params:
            cfgfile -- path to the config file - default: _cfgfile_locations
        """
        return cls._get_instance(cfgfile, force_reload=True)

    @classmethod
    @property
    def workdir(cls) -> str:
        """
        :return: The path of the configured working directory.
        """
        workdir = cls._get_instance().get('workdir')
        assert workdir
        return workdir  # type: ignore

    @classmethod
    def get(cls, key: Optional[str] = None):
        """
        Get a config value or the whole configuration object.

        :param key: Configuration entry to get (default: all entries).
        """
        # pylint: disable=protected-access
        config = cls._get_instance()._config.copy()
        if key:
            return config.get(key)
        return config


# vim:sw=4:ts=4:et:
