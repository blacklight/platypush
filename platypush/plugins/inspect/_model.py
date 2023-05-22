import inspect
import json
import re
from typing import Callable, List, Optional, Type

from platypush.backend import Backend
from platypush.message.event import Event
from platypush.message.response import Response
from platypush.plugins import Plugin
from platypush.utils import get_decorators

from ._parsers import (
    BackendParser,
    EventParser,
    MethodParser,
    Parser,
    PluginParser,
    ResponseParser,
    SchemaParser,
)


class Model:
    """
    Base class for component models.
    """

    _parsers: List[Type[Parser]] = [
        BackendParser,
        EventParser,
        MethodParser,
        PluginParser,
        ResponseParser,
        SchemaParser,
    ]

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
        self.last_modified = last_modified
        self.doc, argsdoc = self._parse_docstring(
            doc or obj_type.__doc__ or '', obj_type=obj_type
        )
        self.args = {}
        self.has_kwargs = False

        for arg in list(inspect.signature(obj_type).parameters.values())[1:]:
            if arg.kind == arg.VAR_KEYWORD:
                self.has_kwargs = True
                continue

            self.args[arg.name] = {
                'default': arg.default
                if not issubclass(arg.default.__class__, type)
                else None,
                'doc': argsdoc.get(arg.name),
            }

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
        for attr in ['name', 'args', 'doc', 'has_kwargs']:
            yield attr, getattr(self, attr)

    @classmethod
    def _parse_docstring(cls, docstring: str, obj_type: type):
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
                continue

            m = re.match(r'^\s*:return:\s+(.*)', line)
            if m:
                if cur_param:
                    params[cur_param] = cur_param_docstring

                new_docstring += '\n\n**Returns:**\n\n' + m.group(1).strip() + ' '
                cur_param = None
                continue

            if cur_param:
                if not line.strip():
                    params[cur_param] = cur_param_docstring
                    cur_param = None
                    cur_param_docstring = ''
                else:
                    cur_param_docstring += '\n' + line.strip() + ' '
            else:
                new_docstring += line + '\n'

        if cur_param:
            params[cur_param] = cur_param_docstring

        for param, doc in params.items():
            params[param] = cls._post_process_docstring(doc, obj_type=obj_type)

        return cls._post_process_docstring(new_docstring, obj_type=obj_type), params

    @classmethod
    def _post_process_docstring(cls, docstring: str, obj_type: type) -> str:
        for parsers in cls._parsers:
            docstring = parsers.parse(docstring, obj_type=obj_type)
        return docstring.strip()


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
        for attr in ['name', 'args', 'actions', 'doc', 'has_kwargs']:
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

    def __init__(self, obj_type: Type[Callable], *args, **kwargs):
        super().__init__(obj_type, name=obj_type.__name__, *args, **kwargs)
