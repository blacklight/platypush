from abc import ABC, abstractmethod
import inspect
import json
import re

from platypush.utils import get_decorators


class Model(ABC):
    def __str__(self):
        return json.dumps(dict(self), indent=2, sort_keys=True)

    def __repr__(self):
        return json.dumps(dict(self))

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
    def __init__(self, backend, prefix=''):
        self.name = backend.__module__[len(prefix) :]
        self.doc = backend.__doc__

    def __iter__(self):
        for attr in ['name', 'doc']:
            yield attr, getattr(self, attr)


class PluginModel(Model):
    def __init__(self, plugin, prefix=''):
        self.name = re.sub(r'\._plugin$', '', plugin.__module__[len(prefix) :])
        self.doc = plugin.__doc__
        self.actions = {
            action_name: ActionModel(getattr(plugin, action_name))
            for action_name in get_decorators(plugin, climb_class_hierarchy=True).get(
                'action', []
            )
        }

    def __iter__(self):
        for attr in ['name', 'actions', 'doc']:
            if attr == 'actions':
                yield attr, {
                    name: dict(action) for name, action in self.actions.items()
                },
            else:
                yield attr, getattr(self, attr)


class EventModel(Model):
    def __init__(self, event, prefix=''):
        self.package = event.__module__[len(prefix) :]
        self.name = event.__name__
        self.doc = event.__doc__

    def __iter__(self):
        for attr in ['name', 'doc']:
            yield attr, getattr(self, attr)


class ResponseModel(Model):
    def __init__(self, response, prefix=''):
        self.package = response.__module__[len(prefix) :]
        self.name = response.__name__
        self.doc = response.__doc__

    def __iter__(self):
        for attr in ['name', 'doc']:
            yield attr, getattr(self, attr)


class ActionModel(Model):
    def __init__(self, action):
        self.name = action.__name__
        self.doc, argsdoc = self._parse_docstring(action.__doc__)
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
    def _parse_docstring(cls, docstring: str):
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
                    params[cur_param] = cur_param_docstring

                cur_param = m.group(1)
                cur_param_docstring = m.group(2)
            elif re.match(r'^\s*:[^:]+:\s*.*', line):
                continue
            else:
                if cur_param:
                    if not line.strip():
                        params[cur_param] = cur_param_docstring
                        cur_param = None
                        cur_param_docstring = ''
                    else:
                        cur_param_docstring += '\n' + line.strip()
                else:
                    new_docstring += line.rstrip() + '\n'

        if cur_param:
            params[cur_param] = cur_param_docstring

        return new_docstring.strip(), params

    def __iter__(self):
        for attr in ['name', 'args', 'doc', 'has_kwargs']:
            yield attr, getattr(self, attr)
