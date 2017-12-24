import json
import random
import threading

from platypush.config import Config
from platypush.message import Message
from platypush.utils import get_event_class_by_type

class Event(Message):
    """ Event message class """

    def __init__(self, target=None, origin=None, id=None, **kwargs):
        """
        Params:
            target  -- Target node [String]
            origin  -- Origin node (default: current node) [String]
            id      -- Event ID (default: auto-generated)
            kwargs  -- Additional arguments for the event [kwDict]
        """

        self.id = id if id else self._generate_id()
        self.target = target if target else Config.get('device_id')
        self.origin = origin if origin else Config.get('device_id')
        self.type = '{}.{}'.format(self.__class__.__module__,
                                   self.__class__.__name__)
        self.args = kwargs

    @classmethod
    def build(cls, msg):
        """ Builds an event message from a JSON UTF-8 string/bytearray, a
        dictionary, or another Event """

        msg = super().parse(msg)
        event_type = msg['args'].pop('type')
        event_class = get_event_class_by_type(event_type)

        args = {
            'target'   : msg['target'],
            'origin'   : msg['origin'],
            **(msg['args'] if 'args' in msg else {}),
        }

        args['id'] = msg['id'] if 'id' in msg else cls._generate_id()
        return event_class(**args)

    def matches_condition(self, condition):
        """
        If the event matches an event condition, it will return an EventMatchResult
        Params:
            -- condition -- The platypush.event.hook.EventCondition object
        """

        result = EventMatchResult(is_match=False)
        if not isinstance(self, condition.type): return result

        for (attr, value) in condition.args.items():
            if not hasattr(self.args, attr):
                return result
            if isinstance(self.args[attr], str) and not value in self.args[attr]:
                return result
            elif self.args[attr] != value:
                return result

        result.is_match = True
        return result


    @staticmethod
    def _generate_id():
        """ Generate a unique event ID """
        id = ''
        for i in range(0,16):
            id += '%.2x' % random.randint(0, 255)
        return id

    def __str__(self):
        """
        Overrides the str() operator and converts
        the message into a UTF-8 JSON string
        """

        return json.dumps({
            'type'     : 'event',
            'target'   : self.target,
            'origin'   : self.origin if hasattr(self, 'origin') else None,
            'id'       : self.id if hasattr(self, 'id') else None,
            'args'     : {
                'type' : self.type,
                **self.args,
            },
        })


class EventMatchResult(object):
    """ When comparing an event against an event condition, you want to
        return this object. It contains the match status (True or False),
        any parsed arguments, and a match_score that identifies how "strong"
        the match is - in case of multiple event matches, the ones with the
        highest score will win """

    def __init__(self, is_match, score=1, parsed_args = {}):
        self.is_match = is_match
        self.score = score
        self.parsed_args = parsed_args


# XXX Should be a stop Request, not an Event
class StopEvent(Event):
    """ StopEvent message. When received on a Bus, it will terminate the
    listening thread having the specified ID. Useful to keep listeners in
    sync and make them quit when the application terminates """

    def __init__(self, target, origin, thread_id, id=None, **kwargs):
        """ Constructor.
        Params:
            target    -- Target node
            origin    -- Origin node
            thread_id -- thread_iden() to be terminated if listening on the bus
            id        -- Event ID (default: auto-generated)
            kwargs    -- Extra key-value arguments
        """

        super().__init__(target=target, origin=origin, id=id,
                         thread_id=thread_id, **kwargs)

    def targets_me(self):
        """ Returns true if the stop event is for the current thread """
        return self.args['thread_id'] == threading.get_ident()


# vim:sw=4:ts=4:et:

