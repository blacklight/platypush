import json
import random

from platypush.message import Message

class Request(Message):
    """ Request message class """

    def __init__(self, target, action, origin=None, id=None, args={}):
        """
        Params:
            target -- Target node [String]
            action -- Action to be executed (e.g. music.mpd.play) [String]
            origin -- Origin node [String]
                id -- Message ID, or None to get it auto-generated
              args -- Additional arguments for the action [Dict]
        """

        self.id = id if id else self._generate_id()
        self.target = target
        self.action = action
        self.origin = origin
        self.args   = args

    @classmethod
    def build(cls, msg):
        msg = super().parse(msg)
        args = {
            'target' : msg['target'],
            'action' : msg['action'],
            'args'   : msg['args'] if 'args' in msg else {},
        }

        if 'origin' in msg: args['origin'] = msg['origin']
        return Request(**args)

    @staticmethod
    def _generate_id():
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
            'type'   : 'request',
            'target' : self.target,
            'action' : self.action,
            'args'   : self.args,
            'origin' : self.origin if hasattr(self, 'origin') else None,
            'id'     : self.id if hasattr(self, 'id') else None,
        })


# vim:sw=4:ts=4:et:

