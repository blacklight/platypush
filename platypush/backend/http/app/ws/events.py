from typing_extensions import override

from platypush.message.event import Event

from . import WSRoute, logger, pubsub_redis_topic
from ..utils import send_message

events_redis_topic = pubsub_redis_topic('events')


class WSEventProxy(WSRoute):
    """
    Websocket event proxy mapped to ``/ws/events``.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subscribe(events_redis_topic)

    @classmethod
    @override
    def app_name(cls) -> str:
        return 'events'

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
                evt = Event.build(msg)
            except Exception as e:
                logger.warning('Error parsing event: %s: %s', msg, e)
                continue

            self.send(str(evt))