from abc import ABC, abstractmethod
import datetime
import logging
import inspect
import json
import time
from typing import Union

logger = logging.getLogger('platypush')


class JSONAble(ABC):
    """
    Generic interface for JSON-able objects.
    """

    @abstractmethod
    def to_json(self) -> Union[str, list, dict]:
        raise NotImplementedError()


class Message(object):
    """ Message generic class """

    class Encoder(json.JSONEncoder):
        @staticmethod
        def parse_numpy(obj):
            try:
                import numpy as np
            except ImportError:
                return

            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if callable(obj):
                return '<function at {}.{}>'.format(obj.__module__, obj.__name__)

            return

        @staticmethod
        def parse_datetime(obj):
            if isinstance(obj, datetime.datetime) or \
                    isinstance(obj, datetime.date) or \
                    isinstance(obj, datetime.time):
                return obj.isoformat()

        def default(self, obj):
            value = self.parse_datetime(obj)
            if value is not None:
                return value

            if isinstance(obj, set):
                return list(obj)

            value = self.parse_numpy(obj)
            if value is not None:
                return value

            if isinstance(obj, JSONAble):
                return obj.to_json()

            try:
                return super().default(obj)
            except Exception as e:
                logger.warning('Could not serialize object type {}: {}: {}'.format(
                    type(obj), str(e), obj))

    def __init__(self, timestamp=None, *args, **kwargs):
        self.timestamp = timestamp or time.time()

    def __str__(self):
        """
        Overrides the str() operator and converts
        the message into a UTF-8 JSON string
        """

        return json.dumps({
            attr: getattr(self, attr)
            for attr in self.__dir__()
            if (attr != '_timestamp' or not attr.startswith('_'))
            and not inspect.ismethod(getattr(self, attr))
        }, cls=self.Encoder).replace('\n', ' ')

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
            # noinspection PyBroadException
            try:
                msg = json.loads(msg.strip())
            except:
                logger.warning('Invalid JSON message: {}'.format(msg))

        assert isinstance(msg, dict)

        if '_timestamp' not in msg:
            msg['_timestamp'] = time.time()

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
        if msgtype != cls:
            return msgtype.build(msg)


class Mapping(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k, v in kwargs.items():
            self.__setattr__(k, v)

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return repr(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __delitem__(self, key):
        del self.__dict__[key]

    def clear(self):
        return self.__dict__.clear()

    def copy(self):
        return self.__dict__.copy()

    def has_key(self, k):
        return k in self.__dict__

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def pop(self, *args):
        return self.__dict__.pop(*args)

    def __cmp__(self, dict_):
        return self.__cmp__(dict_)

    def __contains__(self, item):
        return item in self.__dict__

    def __iter__(self):
        return iter(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


# vim:sw=4:ts=4:et:
