from abc import ABC, abstractmethod
import inspect
import json
import re
from typing import Optional

from platypush.utils import get_decorators


class Model(ABC):
    def __str__(self):
        return json.dumps(dict(self), indent=2, sort_keys=True)

    def __repr__(self):
        return json.dumps(dict(self))

    @staticmethod
    def to_html(doc):
        try:
            import docutils.core  # type: ignore
        except ImportError:
            # docutils not found
            return doc

        return docutils.core.publish_parts(doc, writer_name='html')['html_body']

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError()


class ProcedureEncoder(json.JSONEncoder):
    def default(self, o):
        if callable(o):
            return {
                'type': 'native_function',
            }

        return super().default(o)


class BackendModel(Model):
    def __init__(self, backend, prefix='', html_doc: Optional[bool] = False):
        self.name = backend.__module__[len(prefix) :]
        self.html_doc = html_doc
        self.doc = (
            self.to_html(backend.__doc__)
            if html_doc and backend.__doc__
            else backend.__doc__
        )

    def __iter__(self):
        for attr in ['name', 'doc', 'html_doc']:
            yield attr, getattr(self, attr)


class PluginModel(Model):
    def __init__(self, plugin, prefix='', html_doc: Optional[bool] = False):
        self.name = plugin.__module__[len(prefix) :]
        self.html_doc = html_doc
        self.doc = (
            self.to_html(plugin.__doc__)
            if html_doc and plugin.__doc__
            else plugin.__doc__
        )
        self.actions = {
            action_name: ActionModel(
                getattr(plugin, action_name), html_doc=html_doc or False
            )
            for action_name in get_decorators(plugin, climb_class_hierarchy=True).get(
                'action', []
            )
        }

    def __iter__(self):
        for attr in ['name', 'actions', 'doc', 'html_doc']:
            if attr == 'actions':
                # noinspection PyShadowingNames
                yield attr, {
                    name: dict(action) for name, action in self.actions.items()
                },
            else:
                yield attr, getattr(self, attr)


class EventModel(Model):
    def __init__(self, event, prefix='', html_doc: Optional[bool] = False):
        self.package = event.__module__[len(prefix) :]
        self.name = event.__name__
        self.html_doc = html_doc
        self.doc = (
            self.to_html(event.__doc__) if html_doc and event.__doc__ else event.__doc__
        )

    def __iter__(self):
        for attr in ['name', 'doc', 'html_doc']:
            yield attr, getattr(self, attr)


class ResponseModel(Model):
    def __init__(self, response, prefix='', html_doc: Optional[bool] = False):
        self.package = response.__module__[len(prefix) :]
        self.name = response.__name__
        self.html_doc = html_doc
        self.doc = (
            self.to_html(response.__doc__)
            if html_doc and response.__doc__
            else response.__doc__
        )

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
                'default': arg.default
                if not issubclass(arg.default.__class__, type)
                else None,
                'doc': argsdoc.get(arg.name),
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
                    params[cur_param] = (
                        cls.to_html(cur_param_docstring)
                        if html_doc
                        else cur_param_docstring
                    )

                cur_param = m.group(1)
                cur_param_docstring = m.group(2)
            elif re.match(r'^\s*:[^:]+:\s*.*', line):
                continue
            else:
                if cur_param:
                    if not line.strip():
                        params[cur_param] = (
                            cls.to_html(cur_param_docstring)
                            if html_doc
                            else cur_param_docstring
                        )
                        cur_param = None
                        cur_param_docstring = ''
                    else:
                        cur_param_docstring += '\n' + line.strip()
                else:
                    new_docstring += line.rstrip() + '\n'

        if cur_param:
            params[cur_param] = (
                cls.to_html(cur_param_docstring) if html_doc else cur_param_docstring
            )

        return (
            new_docstring.strip() if not html_doc else cls.to_html(new_docstring),
            params,
        )

    def __iter__(self):
        for attr in ['name', 'args', 'doc', 'has_kwargs']:
            yield attr, getattr(self, attr)
