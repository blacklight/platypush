import json

from platypush.message import Message

class Request(Message):
    """ Request message class """

    def __init__(self, target, action, origin=None, args={}):
        """
        Params:
            target -- Target node [String]
            action -- Action to be executed (e.g. music.mpd.play) [String]
            origin -- Origin node [String]
              args -- Additional arguments for the action [Dict]
        """

        self.target = target
        self.action = action
        self.origin = origin
        self.args   = {}

    @classmethod
    def build(cls, msg):
        msg = super().parse(msg)
        args = {
            'target' : msg['target'],
            'action' : msg['action'],
            'args'   : msg['args'],
        }

        if 'origin' in msg: args['origin'] = msg['origin']
        return Request(**args)

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
        })


# vim:sw=4:ts=4:et:

