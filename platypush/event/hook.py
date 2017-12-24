import json
import logging

from platypush.config import Config
from platypush.message.event import Event
from platypush.message.request import Request
from platypush.utils import get_event_class_by_type


def parse(msg):
    """ Builds a dict given another dictionary or
        a JSON UTF-8 encoded string/bytearray """

    if isinstance(msg, bytes) or isinstance(msg, bytearray):
        msg = msg.decode('utf-8')
    if isinstance(msg, str):
        try:
            msg = json.loads(msg.strip())
        except:
            logging.warning('Invalid JSON message: {}'.format(msg))
            return None

    return msg


class EventCondition(object):
    """ Event hook condition class """

    def __init__(self, type=Event.__class__, **kwargs):
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

        for (key, value) in kwargs.items():
            # TODO So far we only allow simple value match. If value is a dict
            # instead, we should allow more a sophisticated attribute matching,
            # e.g. or conditions, in, and other operators.
            self.args[key] = value

    @classmethod
    def build(cls, rule):
        """ Builds a rule given either another EventRule, a dictionary or
            a JSON UTF-8 encoded string/bytearray """

        if isinstance(rule, cls): return rule
        else: rule = parse(rule)
        assert isinstance(rule, dict)

        type = get_event_class_by_type(
            rule.pop('type') if 'type' in rule else 'Event')

        args = {}
        for (key, value) in rule.items():
            args[key] = value

        return cls(type=type, **args)


class EventAction(Request):
    """ Event hook action class. It is a special type of runnable request
        whose fields can be configured later depending on the event context """

    def __init__(self, target=Config.get('device_id'), action=None, **args):
        super().__init__(target=target, action=action, **args)


    def execute(self, **context):
        for (key, value) in context.items():
            self.args[key] = value

        super().execute()

    @classmethod
    def build(cls, action):
        action = super().parse(action)
        action['origin'] = Config.get('device_id')

        if 'target' not in action:
            action['target'] = action['origin']
        return super().build(action)

class EventHook(object):
    """ Event hook class. It consists of one conditionss and
        one or multiple actions to be executed """

    def __init__(self, name, condition=None, actions=[]):
        """ Construtor. Takes a name, a EventCondition object and a list of
            EventAction objects as input """

        self.name = name
        self.condition = EventCondition.build(condition or {})
        self.actions = actions


    @classmethod
    def build(cls, name, hook):
        """ Builds a rule given either another EventRule, a dictionary or
            a JSON UTF-8 encoded string/bytearray """

        if isinstance(hook, cls): return hook
        else: hook = parse(hook)
        assert isinstance(hook, dict)

        condition = EventCondition.build(hook['if']) if 'if' in hook else None
        actions = []
        if 'then' in hook:
            if isinstance(hook['then'], list):
                actions = [EventAction.build(action) for action in hook['then']]
            else:
                actions = [EventAction.build(hook['then'])]

        return cls(name=name, condition=condition, actions=actions)


    def matches_event(self, event):
        """ Returns an EventMatchResult object containing the information
            about the match between the event and this hook """

        return event.matches_condition(self.condition)


    def run(self, event):
        """ Checks the condition of the hook against a particular event and
            runs the hook actions if the condition is met """

        result = self.matches_event(event)

        if result.is_match:
            logging.info('Running hook {} triggered by an event'.format(self.name))

            for action in self.actions:
                action.execute(**result.parsed_args)


# vim:sw=4:ts=4:et:

