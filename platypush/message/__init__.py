import logging
import inspect
import json

logger = logging.getLogger(__name__)


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
        }).replace('\n', ' ')

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
            try:
                msg = json.loads(msg.strip())
            except:
                logger.warning('Invalid JSON message: {}'.format(msg))

        assert isinstance(msg, dict)
        return msg

    @classmethod
    def build(cls, msg):
        """
        Builds a Message object from a dictionary.
        Params:
            msg -- The message as a key-value dictionary, Message object or JSON string
        """
        from platypush.utils import get_message_class_by_type


        msg = cls.parse(msg)
        msgtype = get_message_class_by_type(msg['type'])
        if msgtype != cls: return msgtype.build(msg)

# vim:sw=4:ts=4:et:

