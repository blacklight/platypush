import json

from platypush.message import Message

class Response(Message):
    """ Response message class """

    def __init__(self, target=None, origin=None, output=None, errors=[]):
        """
        Params:
            target -- Target [String]
            origin -- Origin [String]
            output -- Output [String]
            errors -- Errors [List of strings or exceptions]
        """

        self.target = target
        self.output = output
        self.errors = errors
        self.origin = origin

    def is_error(self):
        """ Returns True if the respopnse has errors """
        return len(self.errors) != 0

    @classmethod
    def build(cls, msg):
        msg = super().parse(msg)
        args = {
            'target' : msg['target'],
            'output' : msg['response']['output'],
            'errors' : msg['response']['errors'],
        }

        if 'origin' in msg: args['origin'] = msg['origin']
        return Response(**args)


    def __str__(self):
        """
        Overrides the str() operator and converts
        the message into a UTF-8 JSON string
        """

        return json.dumps({
            'type'       : 'response',
            'target'     : self.target if hasattr(self, 'target') else None,
            'origin'     : self.origin if hasattr(self, 'origin') else None,
            'response'   : {
                'output' : self.output,
                'errors' : self.errors,
            },
        })

# vim:sw=4:ts=4:et:

