from typing_extensions import override

from platypush.message.event import Event

from . import WSRoute, logger, pubsub_redis_topic

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
    def run(self) -> None:
        for msg in self.listen():
            try:
                evt = Event.build(msg.decode())
            except Exception as e:
                logger.warning('Error parsing event: %s: %s', msg, e)
                continue

            self.send(str(evt))
