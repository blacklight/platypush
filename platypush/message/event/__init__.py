import json
import random
import threading

from enum import Enum

from platypush.message import Message

class Event(Message):
    """ Event message class """

    def __init__(self, target, type, origin, id=None, **kwargs):
        """
        Params:
            target  -- Target node [String]
            type    -- Event type [EventType]
            origin  -- Origin node (default: current node) [String]
                id  -- Event ID (default: auto-generated)
            kwargs  -- Additional arguments for the event [kwDict]
        """

        self.id = id if id else self._generate_id()
        self.target = target
        self.origin = origin
        self.type = type
        self.args = kwargs

    @classmethod
    def build(cls, msg):
        """ Builds an event message from a JSON UTF-8 string/bytearray, a
        dictionary, or another Event """

        msg = super().parse(msg)
        event_type = msg['args'].pop('type')
        event_class = getattr(EventType, event_type).cls

        args = {
            'target'   : msg['target'],
            'origin'   : msg['origin'],
            **(msg['args'] if 'args' in msg else {}),
        }

        args['id'] = msg['id'] if 'id' in msg else cls._generate_id()
        return event_class(**args)

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
                'type' : self.type.name,
                **self.args,
            },
        })


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
                         type=EventType.STOP, thread_id=thread_id, **kwargs)

    def targets_me(self):
        """ Returns true if the stop event is for the current thread """
        return self.args['thread_id'] == threading.get_ident()


class EventType(Enum):
    """ Event types enum """

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, label, cls):
        self.label = label
        self.cls = cls

    STOP = 'STOP', StopEvent


# vim:sw=4:ts=4:et:

