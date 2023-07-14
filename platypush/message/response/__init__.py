import json
import logging
import time

from platypush.message import Message


class Response(Message):
    """Response message class"""

    def __init__(
        self,
        target=None,
        origin=None,
        id=None,
        output=None,
        errors=None,
        timestamp=None,
        logging_level=logging.INFO,
    ):
        """
        :param target: Target
        :type target: str
        :param origin: Origin
        :type origin: str
        :param output: Output
        :param errors: Errors
        :param id: Message ID this response refers to
        :type id: str
        :param timestamp: Message timestamp
        :type timestamp: float
        """

        super().__init__(timestamp=timestamp, logging_level=logging_level)
        self.target = target
        self.output = self._parse_msg(output)
        self.errors = self._parse_msg(errors or [])
        self.origin = origin
        self.id = id
        self._logger = logging.getLogger('platypush:responses')

    def is_error(self):
        """Returns True if the response has errors"""
        return len(self.errors) != 0

    @classmethod
    def _parse_msg(cls, msg):
        if isinstance(msg, (bytes, bytearray)):
            msg = msg.decode('utf-8')
        if isinstance(msg, str):
            try:
                msg = json.loads(msg.strip())
            except ValueError:
                pass

        return msg

    @classmethod
    def build(cls, msg):
        msg = super().parse(msg)
        args = {
            'target': msg['target'],
            'output': msg['response']['output'],
            'errors': msg['response']['errors'],
            'timestamp': msg['_timestamp'] if '_timestamp' in msg else time.time(),
            'logging_level': msg.get('_logging_level', logging.INFO),
        }

        if 'id' in msg:
            args['id'] = msg['id']
        if 'origin' in msg:
            args['origin'] = msg['origin']

        return cls(**args)

    def __str__(self):
        """
        Overrides the ``str()`` operator and converts
        the message into a UTF-8 JSON string
        """
        output = (
            self.output if self.output is not None else {'success': not self.errors}
        )

        response_dict = {
            'id': self.id,
            'type': 'response',
            'target': self.target if hasattr(self, 'target') else None,
            'origin': self.origin if hasattr(self, 'origin') else None,
            '_timestamp': self.timestamp,
            'response': {
                'output': output,
                'errors': self.errors,
            },
        }

        if self.logging_level:
            response_dict['_logging_level'] = self.logging_level

        return json.dumps(response_dict, cls=self.Encoder)

    def log(self, *args, **kwargs):
        self.logging_level = logging.WARNING if self.is_error() else logging.INFO
        super().log(*args, **kwargs)


# vim:sw=4:ts=4:et:
