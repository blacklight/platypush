from abc import ABC, abstractmethod
from dataclasses import asdict, is_dataclass
import decimal
import datetime
from enum import Enum
import io
import logging
import inspect
import json
import time
from typing import Union
from uuid import UUID

_logger = logging.getLogger('platypush')


class JSONAble(ABC):
    """
    Generic interface for JSON-able objects.
    """

    @abstractmethod
    def to_json(self) -> Union[str, list, dict]:
        raise NotImplementedError()


class Message:
    """
    Message generic class
    """

    class Encoder(json.JSONEncoder):
        """
        JSON encoder that can serialize custom types commonly handled in
        Platypush messages.
        """

        @staticmethod
        def parse_numpy(obj):
            try:
                import numpy as np

                if isinstance(obj, np.floating):
                    return float(obj)
                if isinstance(obj, np.integer):
                    return int(obj)
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                if isinstance(obj, decimal.Decimal):
                    return float(obj)
                if isinstance(obj, (bytes, bytearray)):
                    return '0x' + ''.join([f'{x:02x}' for x in obj])
                if callable(obj):
                    return f'<function at {obj.__module__}.{obj.__name__}>'
            except (AttributeError, ImportError, TypeError):
                pass

            return

        @staticmethod
        def parse_datetime(obj):
            if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
                return obj.isoformat()

        def default(self, o):
            from platypush.procedure import Procedure

            value = self.parse_datetime(o)
            if value is not None:
                return value

            if isinstance(o, set):
                return list(o)

            if isinstance(o, UUID):
                return str(o)

            value = self.parse_numpy(o)
            if value is not None:
                return value

            if isinstance(o, JSONAble):
                return o.to_json()

            if isinstance(o, Procedure):
                return o.to_dict()

            if isinstance(o, Enum):
                return o.value

            if isinstance(o, Exception):
                return f'<{o.__class__.__name__}>' + (f' {o}' if o else '')

            if is_dataclass(o):
                return asdict(o)

            if isinstance(o, Message):
                return o.to_dict(o)

            # Don't serialize I/O wrappers/objects
            if isinstance(o, io.IOBase):
                return None

            try:
                return super().default(o)
            except Exception as e:
                _logger.warning(
                    'Could not serialize object type %s: %s: %s', type(o), e, o
                )

    def __init__(self, *_, timestamp=None, logging_level=logging.INFO, **__):
        self.timestamp = timestamp or time.time()
        self.logging_level = logging_level
        self._logger = _logger
        self._default_log_prefix = ''

    def log(self, prefix=''):
        if self.logging_level is None:
            return  # Skip logging

        log_func = self._logger.info
        if self.logging_level == logging.DEBUG:
            log_func = self._logger.debug
        elif self.logging_level == logging.WARNING:
            log_func = self._logger.warning
        elif self.logging_level == logging.ERROR:
            log_func = self._logger.error
        elif self.logging_level == logging.FATAL:
            log_func = self._logger.fatal

        if not prefix:
            prefix = self._default_log_prefix
        log_func('%s%s', prefix, self)

    def __str__(self):
        """
        Overrides the str() operator and converts
        the message into a UTF-8 JSON string
        """

        return json.dumps(
            {
                attr: getattr(self, attr)
                for attr in self.__dir__()
                if (attr != '_timestamp' or not attr.startswith('_'))
                and not inspect.ismethod(getattr(self, attr))
            },
            cls=self.Encoder,
        ).replace('\n', ' ')

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

        :param msg: Original message. It can be a dictionary, a Message,
           or a string/bytearray, as long as it's valid UTF-8 JSON
        """

        if isinstance(msg, cls):
            msg = str(msg)
        if isinstance(msg, (bytes, bytearray)):
            msg = msg.decode('utf-8')
        if isinstance(msg, str):
            try:
                msg = json.loads(msg.strip())
            except (ValueError, TypeError):
                _logger.warning('Invalid JSON message: %s', msg)

        assert isinstance(msg, dict)

        if '_timestamp' not in msg:
            msg['_timestamp'] = time.time()

        return msg

    @classmethod
    def to_dict(cls, msg):
        """
        Converts a Message object into a dictionary

        :param msg: Message object
        """

        return {
            k: v
            for k, v in cls.parse(msg).items()
            if k not in ('id', 'token', 'target', 'origin', '_timestamp')
        }

    @classmethod
    def build(cls, msg):
        """
        Builds a Message object from a dictionary.

        :param msg: The message as a key-value dictionary, Message object or JSON string
        """
        from platypush.utils import get_message_class_by_type

        msg = cls.parse(msg)
        msgtype = get_message_class_by_type(msg['type'])
        if msgtype != cls:
            return msgtype.build(msg)


# vim:sw=4:ts=4:et:
