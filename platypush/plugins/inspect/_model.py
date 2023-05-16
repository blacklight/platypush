import inspect
import json
import re
from typing import Optional, Type

from platypush.backend import Backend
from platypush.message.event import Event
from platypush.message.response import Response
from platypush.plugins import Plugin
from platypush.utils import get_decorators


class Model:
    """
    Base class for component models.
    """

    def __init__(
        self,
        obj_type: type,
        name: Optional[str] = None,
        doc: Optional[str] = None,
        prefix: str = '',
        last_modified: Optional[float] = None,
    ) -> None:
        """
        :param obj_type: Type of the component.
        :param name: Name of the component.
        :param doc: Documentation of the component.
        :param last_modified: Last modified timestamp of the component.
        """
        self._obj_type = obj_type
        self.package = obj_type.__module__[len(prefix) :]
        self.name = name or self.package
        self.doc = doc or obj_type.__doc__
        self.last_modified = last_modified

    def __str__(self):
        """
        :return: JSON string representation of the model.
        """
        return json.dumps(dict(self), indent=2, sort_keys=True)

    def __repr__(self):
        """
        :return: JSON string representation of the model.
        """
        return json.dumps(dict(self))

    def __iter__(self):
        """
        Iterator for the model public attributes/values pairs.
        """
        for attr in ['name', 'doc']:
            yield attr, getattr(self, attr)


# pylint: disable=too-few-public-methods
class BackendModel(Model):
    """
    Model for backend components.
    """

    def __init__(self, obj_type: Type[Backend], *args, **kwargs):
        super().__init__(obj_type, *args, **kwargs)


# pylint: disable=too-few-public-methods
class PluginModel(Model):
    """
    Model for plugin components.
    """

    def __init__(self, obj_type: Type[Plugin], prefix: str = '', **kwargs):
        super().__init__(
            obj_type,
            name=re.sub(r'\._plugin$', '', obj_type.__module__[len(prefix) :]),
            **kwargs,
        )

        self.actions = {
            action_name: ActionModel(getattr(obj_type, action_name))
            for action_name in get_decorators(obj_type, climb_class_hierarchy=True).get(
                'action', []
            )
        }

    def __iter__(self):
        """
        Overrides the default implementation of ``__iter__`` to also include
        plugin actions.
        """
        for attr in ['name', 'actions', 'doc']:
            if attr == 'actions':
                yield attr, {
                    name: dict(action) for name, action in self.actions.items()
                }
            else:
                yield attr, getattr(self, attr)


class EventModel(Model):
    """
    Model for event components.
    """

    def __init__(self, obj_type: Type[Event], **kwargs):
        super().__init__(obj_type, **kwargs)


class ResponseModel(Model):
    """
    Model for response components.
    """

    def __init__(self, obj_type: Type[Response], **kwargs):
        super().__init__(obj_type, **kwargs)


class ActionModel(Model):
    """
    Model for plugin action components.
    """

    def __init__(self, action, **kwargs):
        doc, argsdoc = self._parse_docstring(action.__doc__)
        super().__init__(action, name=action.__name__, doc=doc, **kwargs)

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
