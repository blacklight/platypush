import importlib
import inspect
import json
import os
import pathlib
import pkgutil
from concurrent.futures import Future, ThreadPoolExecutor
from typing import List, Optional

from platypush.backend import Backend
from platypush.common.db import override_definitions
from platypush.common.reflection import Integration, Message as MessageMetadata
from platypush.config import Config
from platypush.plugins import Plugin, action
from platypush.message import Message
from platypush.message.event import Event
from platypush.message.response import Response
from platypush.utils import get_enabled_backends, get_enabled_plugins
from platypush.utils.mock import auto_mocks
from platypush.utils.manifest import Manifest, Manifests, PackageManagers

from ._cache import Cache
from ._serialize import ProcedureEncoder


class InspectPlugin(Plugin):
    """
    This plugin can be used to inspect platypush plugins and backends
    """

    _num_workers = 8
    """Number of threads to use for the inspection."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._cache = Cache()
        self._load_cache()

    @property
    def cache_file(self) -> str:
        """
        :return: The path to the components cache file.
        """
        import platypush

        return os.path.join(
            os.path.dirname(inspect.getfile(platypush)),
            'components.json.gz',
        )

    def _load_cache(self):
        """
        Loads the components cache from disk.
        """
        with self._cache.lock(), auto_mocks(), override_definitions():
            try:
                self._cache = Cache.load(self.cache_file)
            except Exception as e:
                self.logger.warning(
                    'Could not initialize the components cache from %s: %s',
                    self.cache_file,
                    e,
                )

                self.logger.exception(e)

    def refresh_cache(self, force: bool = False):
        """
        Refreshes the components cache.
        """
        cache_version_differs = self._cache.version != Cache.cur_version
        force = force or cache_version_differs

        with self._cache.lock(), auto_mocks(), override_definitions(), ThreadPoolExecutor(
            self._num_workers
        ) as pool:
            futures = []

            for base_type in [Plugin, Backend]:
                futures.append(
                    pool.submit(
                        self._scan_integrations,
                        base_type,
                        pool=pool,
                        force_refresh=force,
                        futures=futures,
                    )
                )

            for base_type in [Event, Response]:
                futures.append(
                    pool.submit(
                        self._scan_modules,
                        base_type,
                        pool=pool,
                        force_refresh=force,
                        futures=futures,
                    )
                )

            while futures:
                futures.pop().result()

        if self._cache.has_changes:
            self.logger.info('Saving new components cache to %s', self.cache_file)
            self._cache.dump(self.cache_file)
            self._cache.loaded_at = self._cache.saved_at

        return self._cache

    def _scan_integration(self, manifest: Manifest):
        """
        Scans a single integration from the manifest and adds it to the cache.
        """
        try:
            self._cache_integration(Integration.from_manifest(manifest.file))
        except Exception as e:
            self.logger.warning(
                'Could not import module %s: %s',
                manifest.package,
                e,
            )

    def _scan_integrations(
        self,
        base_type: type,
        pool: ThreadPoolExecutor,
        futures: List[Future],
        force_refresh: bool = False,
    ):
        """
        Scans the integrations with a manifest file (plugins and backends) and
        refreshes the cache.
        """
        for manifest in Manifests.by_base_class(base_type):
            # An integration metadata needs to be refreshed if it's been
            # modified since it was last loaded, or if it's not in the
            # cache.
            if force_refresh or self._needs_refresh(manifest.file):
                futures.append(pool.submit(self._scan_integration, manifest))

    def _scan_module(self, base_type: type, modname: str):
        """
        Scans a single module for objects that match the given base_type and
        adds them to the cache.
        """
        try:
            module = importlib.import_module(modname)
        except Exception as e:
            self.logger.warning('Could not import module %s: %s', modname, e)
            return

        for _, obj_type in inspect.getmembers(module):
            if (
                inspect.isclass(obj_type)
                and issubclass(obj_type, base_type)
                # Exclude the base_type itself
                and obj_type != base_type
            ):
                self.logger.info(
                    'Scanned %s: %s',
                    base_type.__name__,
                    f'{module.__name__}.{obj_type.__name__}',
                )

                self._cache.set(
                    base_type, obj_type, MessageMetadata.by_type(obj_type).to_dict()
                )

    def _scan_modules(
        self,
        base_type: type,
        pool: ThreadPoolExecutor,
        futures: List[Future],
        force_refresh: bool = False,
    ):
        """
        A generator that scans the modules given a ``base_type`` (e.g. ``Event``).

        It's a bit more inefficient than :meth:`._scan_integrations` because it
        needs to inspect all the members of a module to find the ones that
        match the given ``base_type``, but it works fine for simple components
        (like messages) that don't require extra recursive parsing and don't
        have a manifest.
        """
        prefix = base_type.__module__ + '.'
        path = str(pathlib.Path(inspect.getfile(base_type)).parent)

        for _, modname, __ in pkgutil.walk_packages(
            path=[path], prefix=prefix, onerror=lambda _: None
        ):
            try:
                filename = self._module_filename(path, '.'.join(modname.split('.')[3:]))
                if not (force_refresh or self._needs_refresh(filename)):
                    continue
            except Exception as e:
                self.logger.warning('Could not scan module %s: %s', modname, e)
                continue

            futures.append(pool.submit(self._scan_module, base_type, modname))

    def _needs_refresh(self, filename: str) -> bool:
        """
        :return: True if the given file needs to be refreshed in the cache.
        """
        dirname = os.path.dirname(filename)
        if not os.path.isdir(dirname):
            return True

        return os.lstat(dirname).st_mtime > (self._cache.saved_at or 0)

    @staticmethod
    def _module_filename(path: str, modname: str) -> str:
        """
        :param path: Path to the module.
        :param modname: Module name.
        :return: The full path to the module file.
        """
        filename = os.path.join(path, *modname.split('.')) + '.py'

        if not os.path.isfile(filename):
            filename = os.path.join(path, *modname.split('.'), '__init__.py')

        assert os.path.isfile(filename), f'No such file or directory: {filename}'
        return filename

    def _cache_integration(self, integration: Integration) -> dict:
        """
        :param integration: The :class:`.IntegrationMetadata` object.
        :return: The initialized component's metadata dict.
        """
        self.logger.info(
            'Scanned %s: %s', integration.base_type.__name__, integration.name
        )
        meta = integration.to_dict()
        self._cache.set(integration.base_type, integration.type, meta)
        return meta

    @action
    def get_all_plugins(self):
        """
        Get information about all the available plugins.
        """
        return json.dumps(self._cache.to_dict().get('plugins', {}), cls=Message.Encoder)

    @action
    def get_all_backends(self):
        """
        Get information about all the available backends.
        """
        return json.dumps(
            self._cache.to_dict().get('backends', {}), cls=Message.Encoder
        )

    @action
    def get_all_events(self):
        """
        Get information about all the available events.
        """
        return json.dumps(self._cache.to_dict().get('events', {}), cls=Message.Encoder)

    @action
    def get_all_responses(self):
        """
        Get information about all the available responses.
        """
        return json.dumps(
            self._cache.to_dict().get('responses', {}), cls=Message.Encoder
        )

    @action
    def get_procedures(self) -> dict:
        """
        Get the list of procedures installed on the device.
        """
        return json.loads(json.dumps(Config.get_procedures(), cls=ProcedureEncoder))

    @action
    def get_config(self, entry: Optional[str] = None) -> Optional[dict]:
        """
        Return the configuration of the application or of a section.

        :param entry: [Optional] configuration entry name to retrieve (e.g. ``workdir`` or ``backend.http``).
        :return: The requested configuration object.
        """
        if entry:
            return Config.get(entry)

        return Config.get()

    @action
    def get_enabled_plugins(self) -> List[str]:
        """
        Get the list of enabled plugins.
        """
        return list(get_enabled_plugins().keys())

    @action
    def get_enabled_backends(self) -> List[str]:
        """
        Get the list of enabled backends.
        """
        return list(get_enabled_backends().keys())

    @action
    def get_pkg_managers(self) -> dict:
        """
        Get the list of supported package managers. This is supposed to be an
        internal-only method, only used by the UI to populate the install
        commands.
        """
        pkg_manager = PackageManagers.scan()
        return {
            'items': {
                pkg.value.executable: {
                    'executable': pkg.value.executable,
                    'install': pkg.value.install,
                    'install_doc': pkg.value.install_doc,
                    'uninstall': pkg.value.uninstall,
                    'list': pkg.value.list,
                    'default_os': pkg.value.default_os,
                }
                for pkg in PackageManagers
            },
            'current': pkg_manager.value.executable if pkg_manager else None,
        }


# vim:sw=4:ts=4:et:
