import copy
import json
import logging
import random
import time

from datetime import date

from platypush.config import Config
from platypush.message import Message
from platypush.utils import get_event_class_by_type

logger = logging.getLogger('platypush')


class Event(Message):
    """Event message class"""

    # If this class property is set to false then the logging of these events
    # will be disabled. Logging is usually disabled for events with a very
    # high frequency that would otherwise pollute the logs e.g. camera capture
    # events
    # pylint: disable=redefined-builtin
    def __init__(
        self,
        target=None,
        origin=None,
        id=None,
        timestamp=None,
        logging_level=logging.INFO,
        disable_web_clients_notification=False,
        **kwargs,
    ):
        """
        :param target: Target node
        :type target: str
        :param origin: Origin node (default: current node)
        :type origin: str
        :param id: Event ID (default: auto-generated)
        :type id: str
        :param timestamp: Event timestamp (default: current time)
        :type timestamp: float
        :param logging_level: Logging level for this event (default:
            ``logging.INFO``)
        :param disable_web_clients_notification: Don't send a notification of
            this event to the websocket clients
        :param kwargs: Additional arguments for the event
        """

        super().__init__(timestamp=timestamp, logging_level=logging_level)
        self.id = id if id else self._generate_id()
        self.target = target if target else Config.get('device_id')
        self.origin = origin if origin else Config.get('device_id')
        self.type = f'{self.__class__.__module__}.{self.__class__.__name__}'
        self.args = kwargs
        self.disable_web_clients_notification = disable_web_clients_notification

        for arg, value in self.args.items():
            if arg not in [
                'id',
                'args',
                'origin',
                'target',
                'type',
                'timestamp',
                'logging_level',
            ] and not arg.startswith('_'):
                self.__setattr__(arg, value)

    @classmethod
    def build(cls, msg):
        """
        Builds an event message from a JSON UTF-8 string/bytearray, a
        dictionary, or another Event
        """

        msg = super().parse(msg)
        event_type = msg['args'].pop('type')
        event_class = get_event_class_by_type(event_type)

        args = msg['args'] if 'args' in msg else {}
        args['id'] = msg['id'] if 'id' in msg else cls._generate_id()
        args['target'] = msg['target'] if 'target' in msg else Config.get('device_id')
        args['origin'] = msg['origin'] if 'origin' in msg else Config.get('device_id')
        args['timestamp'] = msg['_timestamp'] if '_timestamp' in msg else time.time()
        return event_class(**args)

    @staticmethod
    def _generate_id():
        """Generate a unique event ID"""
        return ''.join([f'{random.randint(0, 255):02x}' for _ in range(16)])

    def _matches_condition(
        self,
        condition: dict,
        args: dict,
        result: "EventMatchResult",
        match_scores: list,
    ) -> bool:
        for attr, value in condition.items():
            if attr not in args:
                return False

            if isinstance(args[attr], str):
                self._matches_argument(
                    argname=attr, condition_value=value, args=args, result=result
                )

                if result.is_match:
                    match_scores.append(result.score)
                else:
                    return False
            elif isinstance(value, dict):
                if not isinstance(args[attr], dict):
                    return False

                return self._matches_condition(
                    condition=value,
                    args=args[attr],
                    result=result,
                    match_scores=match_scores,
                )
            elif args[attr] != value:
                return False

        return True

    def matches_condition(self, condition):
        """
        If the event matches an event condition, it will return an EventMatchResult
        :param condition: The platypush.event.hook.EventCondition object
        """

        result = EventMatchResult(is_match=False, parsed_args=self.args)
        match_scores = []

        if not isinstance(self, condition.type):
            return result

        if not self._matches_condition(
            condition=condition.args,
            args=self.args,
            result=result,
            match_scores=match_scores,
        ):
            return result

        result.is_match = True
        if match_scores:
            result.score = sum(match_scores) / float(len(match_scores))

        return result

    def _matches_argument(
        self, argname, condition_value, args, result: "EventMatchResult"
    ):
        """
        Returns an EventMatchResult if the event argument [argname] matches
        [condition_value].
        """

        # Simple equality match by default. It can be overridden by the derived classes.
        result.is_match = args.get(argname) == condition_value
        if result.is_match:
            result.score += 2
        else:
            result.score = 0

    def __str__(self):
        """
        Overrides the str() operator and converts
        the message into a UTF-8 JSON string
        """

        args = copy.deepcopy(self.args)
        flatten(args)

        return json.dumps(
            {
                'type': 'event',
                'target': self.target,
                'origin': self.origin if hasattr(self, 'origin') else None,
                'id': self.id if hasattr(self, 'id') else None,
                '_timestamp': self.timestamp,
                'args': {'type': self.type, **args},
            },
            cls=self.Encoder,
        )


class EventMatchResult:
    """
    When comparing an event against an event condition, you want to
    return this object. It contains the match status (True or False),
    any parsed arguments, and a match_score that identifies how "strong"
    the match is - in case of multiple event matches, the ones with the
    highest score will win.
    """

    def __init__(self, is_match, score=0.0, parsed_args=None):
        self.is_match = is_match
        self.score = score
        self.parsed_args = parsed_args or {}


def flatten(args):
    """
    Flatten a nested dictionary for string serialization.
    """
    if isinstance(args, dict):
        for key, value in args.items():
            if isinstance(value, date):
                args[key] = value.isoformat()
            elif isinstance(value, (dict, list)):
                flatten(args[key])
    elif isinstance(args, list):
        for i, arg in enumerate(args):
            if isinstance(arg, date):
                args[i] = arg.isoformat()
            elif isinstance(arg, (dict, list)):
                flatten(args[i])


# vim:sw=4:ts=4:et:
