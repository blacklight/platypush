from logging import getLogger
from threading import Thread
from typing_extensions import override

from redis import ConnectionError
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler

from platypush.config import Config
from platypush.message.event import Event
from platypush.utils import get_redis

events_redis_topic = f'_platypush/{Config.get("device_id")}/events'  # type: ignore
logger = getLogger(__name__)


class WSEventProxy(WebSocketHandler, Thread):
    """
    Websocket event proxy mapped to ``/ws/events``.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sub = get_redis().pubsub()
        self._io_loop = IOLoop.current()

    @override
    def open(self, *_, **__):
        logger.info('Started websocket connection with %s', self.request.remote_ip)
        self.name = f'ws:events@{self.request.remote_ip}'
        self.start()

    @override
    def on_message(self, *_, **__):
        pass

    @override
    def data_received(self, *_, **__):
        pass

    @override
    def run(self) -> None:
        super().run()
        self._sub.subscribe(events_redis_topic)

        try:
            for msg in self._sub.listen():
                if (
                    msg.get('type') != 'message'
                    and msg.get('channel').decode() != events_redis_topic
                ):
                    continue

                try:
                    evt = Event.build(msg.get('data').decode())
                except Exception as e:
                    logger.warning('Error parsing event: %s: %s', msg.get('data'), e)
                    continue

                self._io_loop.asyncio_loop.call_soon_threadsafe(  # type: ignore
                    self.write_message, str(evt)
                )
        except ConnectionError:
            pass

    @override
    def on_close(self):
        self._sub.unsubscribe(events_redis_topic)
        self._sub.close()
        logger.info(
            'Websocket connection to %s closed, reason=%s, message=%s',
            self.request.remote_ip,
            self.close_code,
            self.close_reason,
        )
