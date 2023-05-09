import importlib
import inspect
import json
import pkgutil
import threading
from typing import Optional

import platypush.backend  # lgtm [py/import-and-import-from]
import platypush.plugins  # lgtm [py/import-and-import-from]
import platypush.message.event  # lgtm [py/import-and-import-from]
import platypush.message.response  # lgtm [py/import-and-import-from]

from platypush.backend import Backend
from platypush.config import Config
from platypush.plugins import Plugin, action
from platypush.message.event import Event
from platypush.message.response import Response

from ._model import (
    BackendModel,
    EventModel,
    PluginModel,
    ProcedureEncoder,
    ResponseModel,
)


class InspectPlugin(Plugin):
    """
    This plugin can be used to inspect platypush plugins and backends
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._plugins = {}
        self._backends = {}
        self._events = {}
        self._responses = {}
        self._plugins_lock = threading.RLock()
        self._backends_lock = threading.RLock()
        self._events_lock = threading.RLock()
        self._responses_lock = threading.RLock()
        self._html_doc = False

    def _init_plugins(self):
        package = platypush.plugins
        prefix = package.__name__ + '.'

        for _, modname, _ in pkgutil.walk_packages(
            path=package.__path__, prefix=prefix, onerror=lambda _: None
        ):
            try:
                module = importlib.import_module(modname)
            except Exception as e:
                self.logger.warning('Could not import module %s: %s', modname, e)
                continue

            for _, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, Plugin):
                    model = PluginModel(
                        plugin=obj, prefix=prefix, html_doc=self._html_doc
                    )
                    if model.name:
                        self._plugins[model.name] = model

    def _init_backends(self):
        package = platypush.backend
        prefix = package.__name__ + '.'

        for _, modname, _ in pkgutil.walk_packages(
            path=package.__path__, prefix=prefix, onerror=lambda _: None
        ):
            try:
                module = importlib.import_module(modname)
            except Exception as e:
                self.logger.debug('Could not import module %s: %s', modname, e)
                continue

            for _, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, Backend):
                    model = BackendModel(
                        backend=obj, prefix=prefix, html_doc=self._html_doc
                    )
                    if model.name:
                        self._backends[model.name] = model

    def _init_events(self):
        package = platypush.message.event
        prefix = package.__name__ + '.'

        for _, modname, _ in pkgutil.walk_packages(
            path=package.__path__, prefix=prefix, onerror=lambda _: None
        ):
            try:
                module = importlib.import_module(modname)
            except Exception as e:
                self.logger.debug('Could not import module %s: %s', modname, e)
                continue

            for _, obj in inspect.getmembers(module):
                if type(obj) == Event:  # pylint: disable=unidiomatic-typecheck
                    continue

                if inspect.isclass(obj) and issubclass(obj, Event) and obj != Event:
                    event = EventModel(
                        event=obj, html_doc=self._html_doc, prefix=prefix
                    )
                    if event.package not in self._events:
                        self._events[event.package] = {event.name: event}
                    else:
                        self._events[event.package][event.name] = event

    def _init_responses(self):
        package = platypush.message.response
        prefix = package.__name__ + '.'

        for _, modname, _ in pkgutil.walk_packages(
            path=package.__path__, prefix=prefix, onerror=lambda _: None
        ):
            try:
                module = importlib.import_module(modname)
            except Exception as e:
                self.logger.debug('Could not import module %s: %s', modname, e)
                continue

            for _, obj in inspect.getmembers(module):
                if type(obj) == Response:  # pylint: disable=unidiomatic-typecheck
                    continue

                if (
                    inspect.isclass(obj)
                    and issubclass(obj, Response)
                    and obj != Response
                ):
                    response = ResponseModel(
                        response=obj, html_doc=self._html_doc, prefix=prefix
                    )
                    if response.package not in self._responses:
                        self._responses[response.package] = {response.name: response}
                    else:
                        self._responses[response.package][response.name] = response

    @action
    def get_all_plugins(self, html_doc: Optional[bool] = None):
        """
        :param html_doc: If True then the docstring will be parsed into HTML (default: False)
        """
        with self._plugins_lock:
            if not self._plugins or (
                html_doc is not None and html_doc != self._html_doc
            ):
                self._html_doc = html_doc
                self._init_plugins()

            return json.dumps(
                {name: dict(plugin) for name, plugin in self._plugins.items()}
            )

    @action
    def get_all_backends(self, html_doc: Optional[bool] = None):
        """
        :param html_doc: If True then the docstring will be parsed into HTML (default: False)
        """
        with self._backends_lock:
            if not self._backends or (
                html_doc is not None and html_doc != self._html_doc
            ):
                self._html_doc = html_doc
                self._init_backends()

            return json.dumps(
                {name: dict(backend) for name, backend in self._backends.items()}
            )

    @action
    def get_all_events(self, html_doc: Optional[bool] = None):
        """
        :param html_doc: If True then the docstring will be parsed into HTML (default: False)
        """
        with self._events_lock:
            if not self._events or (
                html_doc is not None and html_doc != self._html_doc
            ):
                self._html_doc = html_doc
                self._init_events()

            return json.dumps(
                {
                    package: {name: dict(event) for name, event in events.items()}
                    for package, events in self._events.items()
                }
            )

    @action
    def get_all_responses(self, html_doc: Optional[bool] = None):
        """
        :param html_doc: If True then the docstring will be parsed into HTML (default: False)
        """
        with self._responses_lock:
            if not self._responses or (
                html_doc is not None and html_doc != self._html_doc
            ):
                self._html_doc = html_doc
                self._init_responses()

            return json.dumps(
                {
                    package: {name: dict(event) for name, event in responses.items()}
                    for package, responses in self._responses.items()
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

        cfg = Config.get()
        return cfg


# vim:sw=4:ts=4:et:
