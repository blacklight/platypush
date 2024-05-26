import datetime
import glob
import importlib
import inspect
import json
import logging
import os
import pathlib
import pkgutil
import re
import shutil
import socket
import sys
from urllib.parse import quote
from typing import Any, Dict, Optional, Set

import yaml

from platypush.utils import (
    get_hash,
    is_functional_procedure,
    is_functional_hook,
    is_functional_cron,
    is_root,
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
    #   - $XDG_CONFIG_HOME/platypush/config.yaml
    #   - $HOME/.config/platypush/config.yaml
    #   - /etc/platypush/config.yaml
    _cfgfile_locations = [
        os.path.join(os.path.abspath('.'), 'config.yaml'),
        os.path.join(os.environ.get('XDG_CONFIG_HOME', ''), 'config.yaml'),
        os.path.join(os.path.expanduser('~'), '.config', 'platypush', 'config.yaml'),
        os.path.join(os.sep, 'etc', 'platypush', 'config.yaml'),
    ]

    # Config singleton instance
    _instance = None

    _default_constants = {
        'today': datetime.date.today,
        'now': datetime.datetime.now,
    }

    # Default working directory:
    #  - $XDG_DATA_HOME/platypush if XDG_DATA_HOME is set
    #  - /var/lib/platypush if the user is root
    #  - $HOME/.local/share/platypush otherwise
    _workdir_location = os.path.join(
        *(
            (os.environ['XDG_DATA_HOME'],)
            if os.environ.get('XDG_DATA_HOME')
            else (
                (os.sep, 'var', 'lib')
                if os.geteuid() == 0
                else (os.path.expanduser('~'), '.local', 'share')
            )
        ),
        'platypush',
    )

    # Default cache directory:
    #  - $XDG_CACHE_DIR/platypush if XDG_CACHE_DIR is set
    #  - /var/cache/platypush if the user is root
    #  - $HOME/.cache/platypush otherwise
    _cachedir_location = os.path.join(
        *(
            (os.environ['XDG_CACHE_DIR'],)
            if os.environ.get('XDG_CACHE_DIR')
            else (
                (os.sep, 'var', 'cache')
                if os.geteuid() == 0
                else (os.path.expanduser('~'), '.cache')
            )
        ),
        'platypush',
    )

    _included_files: Set[str] = set()

    def __init__(
        self,
        cfgfile: Optional[str] = None,
        workdir: Optional[str] = None,
        cachedir: Optional[str] = None,
        db: Optional[str] = None,
    ):
        """
        Constructor. Always use the class as a singleton (i.e. through
        Config.init), you won't probably need to call the constructor directly

        :param cfgfile: Config file path (default: retrieve the first available
            location in _cfgfile_locations).
        :param workdir: Overrides the default working directory.
        :param cachedir: Overrides the default cache directory.
        :param db: Overrides the default database connection string.
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
        self.config_file = ''

        self._init_cfgfile(cfgfile)
        self._config = self._read_config_file(self.config_file)

        self._init_secrets()
        self._init_dirs(workdir=workdir, cachedir=cachedir)
        self._init_db(db=db)
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

        if cfgfile:
            cfgfile = os.path.abspath(os.path.expanduser(cfgfile))

        if cfgfile is None or not os.path.exists(cfgfile):
            cfgfile = self._create_default_config(cfgfile)

        self.config_file = cfgfile

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

    def _init_db(self, db: Optional[str] = None):
        # If the db connection string is passed as an argument, use it
        if db:
            self._config['db'] = {
                'engine': db,
            }
            return

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

    def _init_workdir(self, workdir: Optional[str] = None):
        if workdir:
            self._config['workdir'] = workdir
        if not self._config.get('workdir'):
            self._config['workdir'] = self._workdir_location

        self._config['workdir'] = os.path.expanduser(self._config['workdir'])
        pathlib.Path(self._config['workdir']).mkdir(parents=True, exist_ok=True)

    def _init_cachedir(self, cachedir: Optional[str] = None):
        if cachedir:
            self._config['cachedir'] = cachedir
        if not self._config.get('cachedir'):
            self._config['cachedir'] = self._cachedir_location

        self._config['cachedir'] = os.path.expanduser(self._config['cachedir'])
        pathlib.Path(self._config['cachedir']).mkdir(parents=True, exist_ok=True)

    def _init_scripts_dir(self):
        # Create the scripts directory if it doesn't exist
        if 'scripts_dir' not in self._config:
            self._config['scripts_dir'] = os.path.join(
                os.path.dirname(self.config_file), 'scripts'
            )

        scripts_dir = os.path.abspath(os.path.expanduser(self._config['scripts_dir']))
        os.makedirs(scripts_dir, mode=0o755, exist_ok=True)

        # Make sure that every folder with a .py file has an __init__.py file
        for root, _, files in os.walk(scripts_dir):
            for file in files:
                if file.endswith('.py'):
                    init_py = os.path.join(root, '__init__.py')
                    if not os.path.isfile(init_py):
                        with open(init_py, 'w') as f:
                            f.write('')

        # Include scripts_dir parent in sys.path so members can be imported in scripts
        # through the `scripts` package
        scripts_parent_dir = str(pathlib.Path(scripts_dir).absolute().parent)
        sys.path = [scripts_parent_dir] + sys.path

    def _init_dashboards_dir(self):
        if 'dashboards_dir' not in self._config:
            self._config['dashboards_dir'] = os.path.join(
                os.path.dirname(self.config_file), 'dashboards'
            )
        os.makedirs(self._config['dashboards_dir'], mode=0o755, exist_ok=True)

    def _init_dirs(self, workdir: Optional[str] = None, cachedir: Optional[str] = None):
        self._init_workdir(workdir=workdir)
        self._init_cachedir(cachedir=cachedir)
        self._init_scripts_dir()
        self._init_dashboards_dir()

    def _init_secrets(self):
        if 'token' in self._config:
            self._config['token_hash'] = get_hash(self._config['token'])

    @property
    def _core_plugins(self) -> Dict[str, dict]:
        return {
            'variable': {},
        }

    @staticmethod
    def _create_default_config(cfgfile: Optional[str] = None):
        cfg_mod_dir = os.path.dirname(os.path.abspath(__file__))

        if not cfgfile:
            # Use /etc/platypush/config.yaml if the user is running as root,
            # otherwise ~/.config/platypush/config.yaml
            cfgfile = (
                (
                    os.path.join(os.environ['XDG_CONFIG_HOME'], 'config.yaml')
                    if os.environ.get('XDG_CONFIG_HOME')
                    else os.path.join(
                        os.path.expanduser('~'), '.config', 'platypush', 'config.yaml'
                    )
                )
                if not is_root()
                else os.path.join(os.sep, 'etc', 'platypush', 'config.yaml')
            )

        cfgdir = pathlib.Path(cfgfile).parent
        cfgdir.mkdir(parents=True, exist_ok=True)
        for cf in glob.glob(os.path.join(cfg_mod_dir, 'config*.yaml')):
            shutil.copy(cf, str(cfgdir))

        return cfgfile

    def _read_config_file(self, cfgfile):
        cfgfile_dir = os.path.dirname(os.path.abspath(os.path.expanduser(cfgfile)))
        config = {}

        try:
            with open(cfgfile, 'r') as fp:
                file_config = yaml.safe_load(fp)
        except FileNotFoundError:
            print(f'Unable to open config file {cfgfile}')
            return config

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
                (getattr(obj, 'procedure_name', None) or f'{prefix}{name}'): obj
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

            for mf in pathlib.Path(base_dir).rglob('manifest.json'):
                with open(mf, 'r') as f:
                    manifest = json.load(f).get('manifest')
                    if not manifest:
                        continue

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
        cls,
        cfgfile: Optional[str] = None,
        workdir: Optional[str] = None,
        cachedir: Optional[str] = None,
        db: Optional[str] = None,
        force_reload: bool = False,
    ) -> "Config":
        """
        Lazy getter/setter for the default configuration instance.
        """
        if force_reload or cls._instance is None:
            cfg_args = [cfgfile] if cfgfile else []
            cls._instance = Config(*cfg_args, workdir=workdir, cachedir=cachedir, db=db)
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
    def init(
        cls,
        cfgfile: Optional[str] = None,
        device_id: Optional[str] = None,
        workdir: Optional[str] = None,
        cachedir: Optional[str] = None,
        db: Optional[str] = None,
        ctrl_sock: Optional[str] = None,
        **_,
    ):
        """
        Initializes the config object singleton

        :param cfgfile: Path to the config file (default: _cfgfile_locations)
        :param device_id: Override the configured device_id.
        :param workdir: Override the configured working directory.
        :param cachedir: Override the configured cache directory.
        :param db: Override the configured database connection string.
        :param ctrl_sock: Override the configured control socket.
        """
        cfg = cls._get_instance(
            cfgfile, workdir=workdir, cachedir=cachedir, db=db, force_reload=True
        )
        if device_id:
            cfg.set('device_id', device_id)
        if workdir:
            cfg.set('workdir', workdir)
        if cachedir:
            cfg.set('cachedir', cachedir)
        if db:
            cfg.set('db', db)
        if ctrl_sock:
            cfg.set('ctrl_sock', ctrl_sock)

        return cfg

    @classmethod
    def get_workdir(cls) -> str:
        """
        :return: The path of the configured working directory.
        """
        workdir = cls._get_instance().get('workdir')
        assert workdir
        return workdir  # type: ignore

    @classmethod
    def get_device_id(cls) -> str:
        """
        :return: The configured/default device ID.
        """
        device_id = cls._get_instance().get('device_id')
        assert device_id
        return device_id  # type: ignore

    @classmethod
    def get_cachedir(cls) -> str:
        """
        :return: The path of the configured cache directory.
        """
        workdir = cls._get_instance().get('cachedir')
        assert workdir
        return workdir  # type: ignore

    @classmethod
    def get(cls, key: Optional[str] = None, default: Optional[Any] = None):
        """
        Get a config value or the whole configuration object.

        :param key: Configuration entry to get (default: all entries).
        :param default: Default value to return if the key is missing.
        """
        # pylint: disable=protected-access
        config = cls._get_instance()._config.copy()
        if key:
            return config.get(key, default)
        return config

    @classmethod
    def set(cls, key: str, value: Any):
        """
        Set a config value.

        :param key: Configuration entry to set.
        :param value: New value to set.
        """
        # pylint: disable=protected-access
        cls._get_instance()._config[key] = value

    @classmethod
    def get_file(cls) -> str:
        """
        :return: The main configuration file path.
        """
        return cls._get_instance().config_file


# vim:sw=4:ts=4:et:
