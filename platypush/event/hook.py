import copy
import json
import logging
import threading
from functools import wraps

from platypush.common import exec_wrapper
from platypush.config import Config
from platypush.message.event import Event
from platypush.message.request import Request
from platypush.procedure import Procedure
from platypush.utils import get_event_class_by_type, set_thread_name, is_functional_hook

logger = logging.getLogger('platypush')


def parse(msg):
    """Builds a dict given another dictionary or
    a JSON UTF-8 encoded string/bytearray"""

    if isinstance(msg, (bytes, bytearray)):
        msg = msg.decode('utf-8')
    if isinstance(msg, str):
        try:
            msg = json.loads(msg.strip())
        except json.JSONDecodeError:
            logger.warning('Invalid JSON message: {}'.format(msg))
            return None

    return msg


class EventCondition:
    """Event hook condition class"""

    def __init__(self, type=Event.__class__, priority=None, **kwargs):
        """
        Rule constructor.
        Params:
            type   -- Class of the event to be built
            kwargs -- Fields rules as a key-value (e.g. source_button=btn_id
                or recognized_phrase='Your phrase')
        """

        self.type = type
        self.args = {}
        self.parsed_args = {}
        self.priority = priority

        for (key, value) in kwargs.items():
            # TODO So far we only allow simple value match. If value is a dict
            # instead, we should allow more a sophisticated attribute matching,
            # e.g. or conditions, in, and other operators.
            self.args[key] = value

    @classmethod
    def build(cls, rule):
        """Builds a rule given either another EventRule, a dictionary or
        a JSON UTF-8 encoded string/bytearray"""

        if isinstance(rule, cls):
            return rule
        else:
            rule = parse(rule)

        assert isinstance(rule, dict), f'Not a valid rule: {rule}'
        type = get_event_class_by_type(rule.pop('type') if 'type' in rule else 'Event')

        args = {}
        for (key, value) in rule.items():
            args[key] = value

        return cls(type=type, **args)


class EventAction(Request):
    """Event hook action class. It is a special type of runnable request
    whose fields can be configured later depending on the event context"""

    def __init__(self, target=None, action=None, **args):
        if target is None:
            target = Config.get('device_id')
        args_copy = dict(copy.deepcopy(args))
        super().__init__(target=target, action=action, **args_copy)

    @classmethod
    def build(cls, action):
        action = super().parse(action)
        action['origin'] = Config.get('device_id')

        if 'target' not in action:
            action['target'] = action['origin']

        token = Config.get('token')
        if token:
            action['token'] = token

        return super().build(action)


class EventHook:
    """Event hook class. It consists of one conditions and
    one or multiple actions to be executed"""

    def __init__(self, name, priority=None, condition=None, actions=None):
        """Constructor. Takes a name, a EventCondition object and an event action
        procedure as input. It may also have a priority attached
        as a positive number. If multiple hooks match against an event,
        only the ones that have either the maximum match score or the
        maximum pre-configured priority will be run."""

        self.name = name
        self.condition = EventCondition.build(condition or {})
        self.actions = actions or []
        self.priority = priority or 0
        self.condition.priority = self.priority

    @classmethod
    def build(cls, name, hook):
        """Builds a rule given either another EventRule, a dictionary or
        a JSON UTF-8 encoded string/bytearray"""

        if isinstance(hook, cls):
            return hook
        else:
            hook = parse(hook)

        if is_functional_hook(hook):
            actions = Procedure(name=name, requests=[hook], _async=False)
            return cls(name=name, condition=hook.condition, actions=actions)

        assert isinstance(hook, dict)
        condition = EventCondition.build(hook['if']) if 'if' in hook else None
        actions = []
        priority = hook['priority'] if 'priority' in hook else None
        condition.priority = priority

        if 'then' in hook:
            if isinstance(hook['then'], list):
                actions = hook['then']
            else:
                actions = [hook['then']]

        actions = Procedure.build(name=name + '__Hook', requests=actions, _async=False)
        return cls(name=name, condition=condition, actions=actions, priority=priority)

    def matches_event(self, event):
        """Returns an EventMatchResult object containing the information
        about the match between the event and this hook"""

        return event.matches_condition(self.condition)

    def run(self, event):
        """Checks the condition of the hook against a particular event and
        runs the hook actions if the condition is met"""

        def _thread_func(result):
            set_thread_name('Event-' + self.name)
            self.actions.execute(event=event, **result.parsed_args)

        result = self.matches_event(event)

        if result.is_match:
            logger.info('Running hook {} triggered by an event'.format(self.name))
            threading.Thread(
                target=_thread_func, name='Event-' + self.name, args=(result,)
            ).start()


def hook(event_type=Event, **condition):
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
