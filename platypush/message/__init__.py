import inspect
import json

class Message(object):
    """ Message generic class """

    def __str__(self):
        """
        Overrides the str() operator and converts
        the message into a UTF-8 JSON string
        """

        return json.dumps({
            attr: getattr(self, attr)
            for attr in self.__dir__()
            if not attr.startswith('_')
            and not inspect.ismethod(getattr(self, attr))
        })

    def __bytes__(self):
        """
        Overrides the bytes() operator, converts the message into
        its JSON-serialized UTF-8-encoded representation
        """
        return str(self).encode('utf-8')

    @classmethod
    def parse(cls, msg):
        """
        Parse a generic message into a key-value dictionary
        Params:
            msg -- Original message - can be a dictionary, a Message,
                   or a string/bytearray, as long as it's valid UTF-8 JSON
        """

        if isinstance(msg, cls):
            msg = str(msg)
        if isinstance(msg, bytes) or isinstance(msg, bytearray):
            msg = msg.decode('utf-8')
        if isinstance(msg, str):
            msg = json.loads(msg.strip())

        assert isinstance(msg, dict)
        return msg

    @classmethod
    def build(cls, msg):
        """
        Builds a Message object from a dictionary.
        To be implemented in the derived classes.
        Params:
            msg -- The message as a key-value dictionary
        """
        raise RuntimeError('build should be implemented in a derived class')

# vim:sw=4:ts=4:et:

