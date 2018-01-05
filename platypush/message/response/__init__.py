import json

from platypush.message import Message

class Response(Message):
    """ Response message class """

    def __init__(self, target=None, origin=None, id=None, output=None, errors=[]):
        """
        Params:
            target -- Target [String]
            origin -- Origin [String]
            output -- Output [String]
            errors -- Errors [List of strings or exceptions]
                id -- Message ID this response refers to
        """

        self.target = target
        self.output = self._parse_msg(output)
        self.errors = self._parse_msg(errors)
        self.origin = origin
        self.id = id

    def is_error(self):
        """ Returns True if the respopnse has errors """
        return len(self.errors) != 0

    @classmethod
    def _parse_msg(cls, msg):
        if isinstance(msg, bytes) or isinstance(msg, bytearray):
            msg = msg.decode('utf-8')
        if isinstance(msg, str):
            try: msg = json.loads(msg.strip())
            except ValueError as e: pass

        return msg


    @classmethod
    def build(cls, msg):
        msg = super().parse(msg)
        args = {
            'target' : msg['target'],
            'output' : msg['response']['output'],
            'errors' : msg['response']['errors'],
        }

        if 'id' in msg: args['id'] = msg['id']
        if 'origin' in msg: args['origin'] = msg['origin']
        return cls(**args)


    def __str__(self):
        """
        Overrides the str() operator and converts
        the message into a UTF-8 JSON string
        """

        return json.dumps({
            'id'         : self.id,
            'type'       : 'response',
            'target'     : self.target if hasattr(self, 'target') else None,
            'origin'     : self.origin if hasattr(self, 'origin') else None,
            'response'   : {
                'output' : self.output,
                'errors' : self.errors,
            },
        })

# vim:sw=4:ts=4:et:

