from collections import defaultdict
import importlib
import inspect
import json
import os
import pathlib
import pickle
import pkgutil
from types import ModuleType
from typing import Callable, Dict, Generator, Optional, Type, Union

from platypush.backend import Backend
from platypush.config import Config
from platypush.plugins import Plugin, action
from platypush.message.event import Event
from platypush.message.response import Response
from platypush.utils import (
    get_backend_class_by_name,
    get_backend_name_by_class,
    get_plugin_class_by_name,
    get_plugin_name_by_class,
)
from platypush.utils.manifest import Manifest, scan_manifests

from ._context import ComponentContext
from ._model import (
    BackendModel,
    EventModel,
    Model,
    PluginModel,
    ResponseModel,
)
from ._serialize import ProcedureEncoder


class InspectPlugin(Plugin):
    """
    This plugin can be used to inspect platypush plugins and backends
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._components_cache_file = os.path.join(
            Config.get('workdir'),  # type: ignore
            'components.cache',  # type: ignore
        )
        self._components_context: Dict[type, ComponentContext] = defaultdict(
            ComponentContext
        )
        self._components_cache: Dict[type, dict] = defaultdict(dict)
        self._load_components_cache()

    def _load_components_cache(self):
        """
        Loads the components cache from disk.
        """
        try:
            with open(self._components_cache_file, 'rb') as f:
                self._components_cache = pickle.load(f)
        except Exception as e:
            self.logger.warning('Could not initialize the components cache: %s', e)
            self.logger.info(
                'The plugin will initialize the cache by scanning '
                'the integrations at the next run. This may take a while'
            )

    def _flush_components_cache(self):
        """
        Flush the current components cache to disk.
        """
        with open(self._components_cache_file, 'wb') as f:
            pickle.dump(self._components_cache, f)

    def _get_cached_component(
        self, base_type: type, comp_type: type
    ) -> Optional[Model]:
        """
        Retrieve a cached component's ``Model``.

        :param base_type: The base type of the component (e.g. ``Plugin`` or
            ``Backend``).
        :param comp_type: The specific type of the component (e.g.
            ``MusicMpdPlugin`` or ``HttpBackend``).
        :return: The cached component's ``Model`` if it exists, otherwise null.
        """
        return self._components_cache.get(base_type, {}).get(comp_type)

    def _cache_component(
        self,
        base_type: type,
        comp_type: type,
        model: Model,
        index_by_module: bool = False,
    ):
        """
        Cache the ``Model`` object for a component.

        :param base_type: The base type of the component (e.g. ``Plugin`` or
            ``Backend``).
        :param comp_type: The specific type of the component (e.g.
            ``MusicMpdPlugin`` or ``HttpBackend``).
        :param model: The ``Model`` object to cache.
        :param index_by_module: If ``True``, the ``Model`` object will be
            indexed according to the ``base_type -> module -> comp_type``
            mapping, otherwise ``base_type -> comp_type``.
        """
        if index_by_module:
            if not self._components_cache.get(base_type, {}).get(model.package):
                self._components_cache[base_type][model.package] = {}
            self._components_cache[base_type][model.package][comp_type] = model
        else:
            self._components_cache[base_type][comp_type] = model

    def _scan_integrations(self, base_type: type):
        """
        A generator that scans the manifest files given a ``base_type``
        (``Plugin`` or ``Backend``) and yields the parsed submodules.
        """
        for mf_file in scan_manifests(base_type):
            manifest = Manifest.from_file(mf_file)
            try:
                yield importlib.import_module(manifest.package)
            except Exception as e:
                self.logger.debug(
                    'Could not import module %s: %s',
                    manifest.package,
                    e,
                )
                continue

    def _scan_modules(self, base_type: type) -> Generator[ModuleType, None, None]:
        """
        A generator that scan the modules given a ``base_type`` (e.g. ``Event``).

        Unlike :meth:`._scan_integrations`, this method recursively scans the
        modules using ``pkgutil`` instead of using the information provided in
        the integrations' manifest files.
        """
        prefix = base_type.__module__ + '.'
        path = str(pathlib.Path(inspect.getfile(base_type)).parent)

        for _, modname, _ in pkgutil.walk_packages(
            path=[path], prefix=prefix, onerror=lambda _: None
        ):
            try:
                yield importlib.import_module(modname)
            except Exception as e:
                self.logger.debug('Could not import module %s: %s', modname, e)
                continue

    def _init_component(
        self,
        base_type: type,
        comp_type: type,
        model_type: Type[Model],
        index_by_module: bool = False,
    ) -> Model:
        """
        Initialize a component's ``Model`` object and cache it.

        :param base_type: The base type of the component (e.g. ``Plugin`` or
            ``Backend``).
        :param comp_type: The specific type of the component (e.g.
            ``MusicMpdPlugin`` or ``HttpBackend``).
        :param model_type: The type of the ``Model`` object that should be
            created.
        :param index_by_module: If ``True``, the ``Model`` object will be
            indexed according to the ``base_type -> module -> comp_type``
            mapping, otherwise ``base_type -> comp_type``.
        :return: The initialized component's ``Model`` object.
        """
        prefix = base_type.__module__ + '.'
        comp_file = inspect.getsourcefile(comp_type)
        model = None
        mtime = None

        if comp_file:
            mtime = os.stat(comp_file).st_mtime
            cached_model = self._get_cached_component(base_type, comp_type)

            # Only update the component model if its source file was
            # modified since the last time it was scanned
            if (
                cached_model
                and cached_model.last_modified
                and mtime <= cached_model.last_modified
            ):
                model = cached_model

        if not model:
            self.logger.info('Scanning component %s', comp_type.__name__)
            model = model_type(comp_type, prefix=prefix, last_modified=mtime)

        self._cache_component(
            base_type, comp_type, model, index_by_module=index_by_module
        )
        return model

    def _init_modules(
        self,
        base_type: type,
        model_type: Type[Model],
    ):
        """
        Initializes, parses and caches all the components of a given type.

        Unlike :meth:`._scan_integrations`, this method inspects all the
        members of a ``module`` for those that match the given ``base_type``
        instead of relying on the information provided in the manifest.

        It is a bit more inefficient, but it works fine for simple components
        (like entities and messages) that don't require extra recursive parsing
        logic for their docs (unlike plugins).
        """
        for module in self._scan_modules(base_type):
            for _, obj_type in inspect.getmembers(module):
                if (
                    inspect.isclass(obj_type)
                    and issubclass(obj_type, base_type)
                    # Exclude the base_type itself
                    and obj_type != base_type
                ):
                    self._init_component(
                        base_type=base_type,
                        comp_type=obj_type,
                        model_type=model_type,
                        index_by_module=True,
                    )

    def _init_integrations(
        self,
        base_type: Type[Union[Plugin, Backend]],
        model_type: Type[Union[PluginModel, BackendModel]],
        class_by_name: Callable[[str], Optional[type]],
    ):
        """
        Initializes, parses and caches all the integrations of a given type.

        :param base_type: The base type of the component (e.g. ``Plugin`` or
            ``Backend``).
        :param model_type: The type of the ``Model`` objects that should be
            created.
        :param class_by_name: A function that returns the class of a given
            integration given its qualified name.
        """
        for module in self._scan_integrations(base_type):
            comp_name = '.'.join(module.__name__.split('.')[2:])
            comp_type = class_by_name(comp_name)
            if not comp_type:
                continue

            self._init_component(
                base_type=base_type,
                comp_type=comp_type,
                model_type=model_type,
            )

        self._flush_components_cache()

    def _init_plugins(self):
        """
        Initializes and caches all the available plugins.
        """
        self._init_integrations(
            base_type=Plugin,
            model_type=PluginModel,
            class_by_name=get_plugin_class_by_name,
        )

    def _init_backends(self):
        """
        Initializes and caches all the available backends.
        """
        self._init_integrations(
            base_type=Backend,
            model_type=BackendModel,
            class_by_name=get_backend_class_by_name,
        )

    def _init_events(self):
        """
        Initializes and caches all the available events.
        """
        self._init_modules(
            base_type=Event,
            model_type=EventModel,
        )

    def _init_responses(self):
        """
        Initializes and caches all the available responses.
        """
        self._init_modules(
            base_type=Response,
            model_type=ResponseModel,
        )

    def _init_components(self, base_type: type, initializer: Callable[[], None]):
        """
        Context manager boilerplate for the other ``_init_*`` methods.
        """
        ctx = self._components_context[base_type]
        with ctx.init_lock:
            if not ctx.refreshed.is_set():
                initializer()
                ctx.refreshed.set()

    @action
    def get_all_plugins(self):
        """
        Get information about all the available plugins.
        """
        self._init_components(Plugin, self._init_plugins)
        return json.dumps(
            {
                get_plugin_name_by_class(cls): dict(plugin)
                for cls, plugin in self._components_cache.get(Plugin, {}).items()
            }
        )

    @action
    def get_all_backends(self):
        """
        Get information about all the available backends.
        """
        self._init_components(Backend, self._init_backends)
        return json.dumps(
            {
                get_backend_name_by_class(cls): dict(backend)
                for cls, backend in self._components_cache.get(Backend, {}).items()
            }
        )

    @action
    def get_all_events(self):
        """
        Get information about all the available events.
        """
        self._init_components(Event, self._init_events)
        return json.dumps(
            {
                package: {
                    obj_type.__name__: dict(event_model)
                    for obj_type, event_model in events.items()
                }
                for package, events in self._components_cache.get(Event, {}).items()
            }
        )

    @action
    def get_all_responses(self):
        """
        Get information about all the available responses.
        """
        self._init_components(Response, self._init_responses)
        return json.dumps(
            {
                package: {
                    obj_type.__name__: dict(response_model)
                    for obj_type, response_model in responses.items()
                }
                for package, responses in self._components_cache.get(
                    Response, {}
                ).items()
            }
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


# vim:sw=4:ts=4:et:
