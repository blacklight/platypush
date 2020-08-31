import importlib
import inspect
import json
import pkgutil
import re
import threading
from typing import Optional

import platypush.backend
import platypush.plugins
import platypush.message.event
import platypush.message.response

from platypush.backend import Backend
from platypush.config import Config
from platypush.plugins import Plugin, action
from platypush.message.event import Event
from platypush.message.response import Response
from platypush.utils import get_decorators


# noinspection PyTypeChecker
class Model:
    def __str__(self):
        return json.dumps(dict(self), indent=2, sort_keys=True)

    def __repr__(self):
        return json.dumps(dict(self))

    @staticmethod
    def to_html(doc):
        try:
            import docutils.core
        except ImportError:
            # docutils not found
            return doc

        return docutils.core.publish_parts(doc, writer_name='html')['html_body']


class ProcedureEncoder(json.JSONEncoder):
    def default(self, o):
        if callable(o):
            return {
                'type': 'native_function',
            }

        return super().default(o)


class BackendModel(Model):
    def __init__(self, backend, prefix='', html_doc: bool = False):
        self.name = backend.__module__[len(prefix):]
        self.html_doc = html_doc
        self.doc = self.to_html(backend.__doc__) if html_doc and backend.__doc__ else backend.__doc__

    def __iter__(self):
        for attr in ['name', 'doc', 'html_doc']:
            yield attr, getattr(self, attr)


class PluginModel(Model):
    def __init__(self, plugin, prefix='', html_doc: bool = False):
        self.name = plugin.__module__[len(prefix):]
        self.html_doc = html_doc
        self.doc = self.to_html(plugin.__doc__) if html_doc and plugin.__doc__ else plugin.__doc__
        self.actions = {action_name: ActionModel(getattr(plugin, action_name), html_doc=html_doc)
                        for action_name in get_decorators(plugin, climb_class_hierarchy=True).get('action', [])}

    def __iter__(self):
        for attr in ['name', 'actions', 'doc', 'html_doc']:
            if attr == 'actions':
                # noinspection PyShadowingNames
                yield attr, {name: dict(action) for name, action in self.actions.items()},
            else:
                yield attr, getattr(self, attr)


class EventModel(Model):
    def __init__(self, event, html_doc: bool = False):
        self.package = event.__module__
        self.name = event.__name__
        self.html_doc = html_doc
        self.doc = self.to_html(event.__doc__) if html_doc and event.__doc__ else event.__doc__

    def __iter__(self):
        for attr in ['name', 'doc', 'html_doc']:
            yield attr, getattr(self, attr)


class ResponseModel(Model):
    def __init__(self, response, html_doc: bool = False):
        self.package = response.__module__
        self.name = response.__name__
        self.html_doc = html_doc
        self.doc = self.to_html(response.__doc__) if html_doc and response.__doc__ else response.__doc__

    def __iter__(self):
        for attr in ['name', 'doc', 'html_doc']:
            yield attr, getattr(self, attr)


class ActionModel(Model):
    # noinspection PyShadowingNames
    def __init__(self, action, html_doc: bool = False):
        self.name = action.__name__
        self.doc, argsdoc = self._parse_docstring(action.__doc__, html_doc=html_doc)
        self.args = {}
        self.has_kwargs = False

        for arg in list(inspect.signature(action).parameters.values())[1:]:
            if arg.kind == arg.VAR_KEYWORD:
                self.has_kwargs = True
                continue

            self.args[arg.name] = {
                'default': arg.default if not issubclass(arg.default.__class__, type) else None,
                'doc': argsdoc.get(arg.name)
            }

    @classmethod
    def _parse_docstring(cls, docstring: str, html_doc: bool = False):
        new_docstring = ''
        params = {}
        cur_param = None
        cur_param_docstring = ''

        if not docstring:
            return None, {}

        for line in docstring.split('\n'):
            m = re.match(r'^\s*:param ([^:]+):\s*(.*)', line)
            if m:
                if cur_param:
                    params[cur_param] = cls.to_html(cur_param_docstring) if html_doc else cur_param_docstring

                cur_param = m.group(1)
                cur_param_docstring = m.group(2)
            elif re.match(r'^\s*:[^:]+:\s*.*', line):
                continue
            else:
                if cur_param:
                    if not line.strip():
                        params[cur_param] = cls.to_html(cur_param_docstring) if html_doc else cur_param_docstring
                        cur_param = None
                        cur_param_docstring = ''
                    else:
                        cur_param_docstring += '\n' + line.strip()
                else:
                    new_docstring += line.rstrip() + '\n'

        if cur_param:
            params[cur_param] = cls.to_html(cur_param_docstring) if html_doc else cur_param_docstring

        return new_docstring.strip() if not html_doc else cls.to_html(new_docstring), params

    def __iter__(self):
        for attr in ['name', 'args', 'doc', 'has_kwargs']:
            yield attr, getattr(self, attr)


class InspectPlugin(Plugin):
    """
    This plugin can be used to inspect platypush plugins and backends

    Requires:

        * **docutils** (``pip install docutils``) - optional, for HTML doc generation

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

        for _, modname, _ in pkgutil.walk_packages(path=package.__path__,
                                                   prefix=prefix,
                                                   onerror=lambda x: None):
            # noinspection PyBroadException
            try:
                module = importlib.import_module(modname)
            except:
                continue

            for _, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, Plugin):
                    model = PluginModel(plugin=obj, prefix=prefix, html_doc=self._html_doc)
                    if model.name:
                        self._plugins[model.name] = model

    def _init_backends(self):
        package = platypush.backend
        prefix = package.__name__ + '.'

        for _, modname, _ in pkgutil.walk_packages(path=package.__path__,
                                                   prefix=prefix,
                                                   onerror=lambda x: None):
            # noinspection PyBroadException
            try:
                module = importlib.import_module(modname)
            except:
                continue

            for _, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, Backend):
                    model = BackendModel(backend=obj, prefix=prefix, html_doc=self._html_doc)
                    if model.name:
                        self._backends[model.name] = model

    def _init_events(self):
        package = platypush.message.event
        prefix = package.__name__ + '.'

        for _, modname, _ in pkgutil.walk_packages(path=package.__path__,
                                                   prefix=prefix,
                                                   onerror=lambda x: None):
            # noinspection PyBroadException
            try:
                module = importlib.import_module(modname)
            except:
                continue

            for _, obj in inspect.getmembers(module):
                if type(obj) == Event:
                    continue

                if inspect.isclass(obj) and issubclass(obj, Event):
                    event = EventModel(event=obj, html_doc=self._html_doc)
                    if event.package not in self._events:
                        self._events[event.package] = {event.name: event}
                    else:
                        self._events[event.package][event.name] = event

    def _init_responses(self):
        package = platypush.message.response
        prefix = package.__name__ + '.'

        for _, modname, _ in pkgutil.walk_packages(path=package.__path__,
                                                   prefix=prefix,
                                                   onerror=lambda x: None):
            # noinspection PyBroadException
            try:
                module = importlib.import_module(modname)
            except:
                continue

            for _, obj in inspect.getmembers(module):
                if type(obj) == Response:
                    continue

                if inspect.isclass(obj) and issubclass(obj, Response):
                    response = ResponseModel(response=obj, html_doc=self._html_doc)
                    if response.package not in self._responses:
                        self._responses[response.package] = {response.name: response}
                    else:
                        self._responses[response.package][response.name] = response

    @action
    def get_all_plugins(self, html_doc: bool = None):
        """
        :param html_doc: If True then the docstring will be parsed into HTML (default: False)
        """
        with self._plugins_lock:
            if not self._plugins or (html_doc is not None and html_doc != self._html_doc):
                self._html_doc = html_doc
                self._init_plugins()

            return json.dumps({
                name: dict(plugin)
                for name, plugin in self._plugins.items()
            })

    @action
    def get_all_backends(self, html_doc: bool = None):
        """
        :param html_doc: If True then the docstring will be parsed into HTML (default: False)
        """
        with self._backends_lock:
            if not self._backends or (html_doc is not None and html_doc != self._html_doc):
                self._html_doc = html_doc
                self._init_backends()

            return json.dumps({
                name: dict(backend)
                for name, backend in self._backends.items()
            })

    @action
    def get_all_events(self, html_doc: bool = None):
        """
        :param html_doc: If True then the docstring will be parsed into HTML (default: False)
        """
        with self._events_lock:
            if not self._events or (html_doc is not None and html_doc != self._html_doc):
                self._html_doc = html_doc
                self._init_events()

            return json.dumps({
                package: {
                    name: dict(event)
                    for name, event in self._events[package].items()
                }
                for package, events in self._events.items()
            })

    @action
    def get_all_responses(self, html_doc: bool = None):
        """
        :param html_doc: If True then the docstring will be parsed into HTML (default: False)
        """
        with self._responses_lock:
            if not self._responses or (html_doc is not None and html_doc != self._html_doc):
                self._html_doc = html_doc
                self._init_responses()

            return json.dumps({
                package: {
                    name: dict(event)
                    for name, event in self._responses[package].items()
                }
                for package, events in self._responses.items()
            })

    @action
    def get_procedures(self) -> dict:
        """
        Get the list of procedures installed on the device.
        """
        return json.loads(json.dumps(Config.get_procedures(), cls=ProcedureEncoder))

    @action
    def get_config(self, entry: Optional[str] = None) -> dict:
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
