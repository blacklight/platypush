from typing_extensions import override

from platypush.backend.http.app.mixins import MessageType
from platypush.message.event import Event

from . import WSRoute, logger
from ..utils import send_message


class WSEventProxy(WSRoute):
    """
    Websocket event proxy mapped to ``/ws/events``.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, subscriptions=[self.events_channel], **kwargs)

    @classmethod
    @override
    def app_name(cls) -> str:
        return 'events'

    @classmethod
    @property
    def events_channel(cls) -> str:
        return cls.get_channel('events')

    @override
    @classmethod
    def publish(cls, data: MessageType, *_) -> None:
        super().publish(data, cls.events_channel)

    @override
    def on_message(self, message):
        try:
            event = Event.build(message)
            assert isinstance(event, Event), f'Expected {Event}, got {type(event)}'
        except Exception as e:
            logger.info('Could not build event from %s: %s', message, e)
            logger.exception(e)
            return

        send_message(event, wait_for_response=False)

    @override
    def run(self) -> None:
        for msg in self.listen():
            try:
                evt = Event.build(msg.data)
            except Exception as e:
                logger.warning('Error parsing event: %s: %s', msg, e)
                continue

            self.send(evt)
