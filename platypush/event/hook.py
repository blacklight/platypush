import copy
import json
import importlib
import logging
import threading
from functools import wraps
from typing import Optional, Type

from platypush.common import exec_wrapper
from platypush.config import Config
from platypush.message.event import Event
from platypush.message.request import Request
from platypush.procedure import Procedure
from platypush.utils import get_event_class_by_type, is_functional_hook

logger = logging.getLogger('platypush')


def parse(msg):
    """
    Builds a dict given another dictionary or a JSON UTF-8 encoded
    string/bytearray.
    """

    if isinstance(msg, (bytes, bytearray)):
        msg = msg.decode('utf-8')
    if isinstance(msg, str):
        try:
            msg = json.loads(msg.strip())
        except json.JSONDecodeError:
            logger.warning('Invalid JSON message: %s', msg)
            return None

    return msg


# pylint: disable=too-few-public-methods
class EventCondition:
    """Event hook condition class"""

    # pylint: disable=redefined-builtin
    def __init__(self, type: Optional[Type[Event]] = None, priority=None, **kwargs):
        """
        Rule constructor.
        Params:
            type   -- Class of the event to be built
            kwargs -- Fields rules as a key-value (e.g. source_button=btn_id
                or recognized_phrase='Your phrase')
        """
        self.type = self._get_event_type(type)
        self.args = {}
        self.parsed_args = {}
        self.priority = priority

        for key, value in kwargs.items():
            self.args[key] = value

    @staticmethod
    def _get_event_type(type: Optional[Type[Event]] = None) -> Type[Event]:
        if not type:
            return Event

        # The package alias `platypush.events` -> `platypush.message.event` is
        # supported
        if type.__module__.startswith('platypush.events'):
            module = importlib.import_module(
                'platypush.message.event' + type.__module__[len('platypush.events') :]
            )

            type = getattr(module, type.__name__)
            assert type, f'Invalid event type: {type}'

        return type

    @classmethod
    def build(cls, rule):
        """
        Builds a rule given either another EventRule, a dictionary or a JSON
        UTF-8 encoded string/bytearray.
        """

        if isinstance(rule, cls):
            return rule

        rule = parse(rule)
        assert isinstance(rule, dict), f'Not a valid rule: {rule}'
        type = get_event_class_by_type(rule.pop('type') if 'type' in rule else 'Event')

        args = {}
        for key, value in rule.items():
            args[key] = value

        return cls(type=type, **args)


class EventAction(Request):
    """
    Event hook action class. It is a special type of runnable request whose
    fields can be configured later depending on the event context.
    """

    def __init__(self, target=None, action=None, **args):
        if target is None:
            target = Config.get('device_id')
        args_copy = dict(copy.deepcopy(args))
        super().__init__(target=target, action=action, **args_copy)

    @classmethod
    def build(cls, msg):
        msg = super().parse(msg)
        msg['origin'] = Config.get('device_id')

        if 'target' not in msg:
            msg['target'] = msg['origin']

        token = Config.get('token')
        if token:
            msg['token'] = token

        return super().build(msg)


class EventHook:
    """
    Event hook class. It consists of one conditions and one or multiple actions
    to be executed.
    """

    def __init__(self, name, priority=None, condition=None, actions=None):
        """
        Takes a name, a EventCondition object and an event action procedure as
        input. It may also have a priority attached as a positive number. If
        multiple hooks match against an event, only the ones that have either
        the maximum match score or the maximum pre-configured priority will be
        run.
        """

        self.name = name
        self.condition = EventCondition.build(condition or {})
        self.actions = actions or []
        self.priority = priority or 0
        self.condition.priority = self.priority

    @classmethod
    def build(cls, name, hook):  # pylint: disable=redefined-outer-name
        """
        Builds a rule given either another EventRule, a dictionary or a JSON
        UTF-8 encoded string/bytearray.
        """

        if isinstance(hook, cls):
            return hook

        hook = parse(hook)
        if is_functional_hook(hook):
            actions = Procedure(name=name, requests=[hook], _async=False)
            return cls(
                name=name, condition=getattr(hook, 'condition', None), actions=actions
            )

        assert isinstance(hook, dict)
        condition = EventCondition.build(hook['if']) if 'if' in hook else None
        actions = []
        priority = hook['priority'] if 'priority' in hook else None
        if condition:
            condition.priority = priority

        if 'then' in hook:
            if isinstance(hook['then'], list):
                actions = hook['then']
            else:
                actions = [hook['then']]

        actions = Procedure.build(name=name + '__Hook', requests=actions, _async=False)
        return cls(name=name, condition=condition, actions=actions, priority=priority)

    def matches_event(self, event):
        """
        Returns an EventMatchResult object containing the information about the
        match between the event and this hook.
        """

        return event.matches_condition(self.condition)

    def run(self, event):
        """
        Checks the condition of the hook against a particular event and runs
        the hook actions if the condition is met.
        """

        def _thread_func(result):
            executor = getattr(self.actions, 'execute', None)
            if executor and callable(executor):
                executor(event=event, **result.parsed_args)

        result = self.matches_event(event)

        if result.is_match:
            logger.info(
                'Running hook `%s` triggered by a `%s` event',
                self.name,
                f'{event.__module__}.{event.__class__.__name__}',
            )

            threading.Thread(
                target=_thread_func,
                name='Event-' + self.name,
                args=(result,),
                daemon=True,
            ).start()


def hook(event_type=Event, **condition):
    """
    Decorator used for event hook functions.
    """

    def wrapper(f):
        f.hook = True
        f.condition = EventCondition(type=event_type, **condition)

        @wraps(f)
        def wrapped(event, *args, **kwargs):
            from platypush.message.event.http.hook import WebhookEvent

            response = exec_wrapper(f, event, *args, **kwargs)
            if isinstance(event, WebhookEvent):
                event.send_response(response)

            return response

        return wrapped

    return wrapper


# vim:sw=4:ts=4:et:
