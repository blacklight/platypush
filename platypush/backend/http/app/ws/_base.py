from abc import ABC, abstractclassmethod
import json
from logging import getLogger
from threading import RLock, Thread
from typing import Any, Generator, Iterable, Optional, Union
from typing_extensions import override

from redis import ConnectionError as RedisConnectionError
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler

from platypush.backend.http.app.utils.auth import AuthStatus, get_auth_status
from platypush.config import Config
from platypush.message import Message
from platypush.utils import get_redis

logger = getLogger(__name__)


def pubsub_redis_topic(topic: str) -> str:
    return f'_platypush/{Config.get("device_id")}/{topic}'  # type: ignore


class WSRoute(WebSocketHandler, Thread, ABC):
    """
    Base class for Tornado websocket endpoints.
    """

    def __init__(self, *args, redis_topics: Optional[Iterable[str]] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._redis_topics = set(redis_topics or [])
        self._sub = get_redis().pubsub()
        self._io_loop = IOLoop.current()
        self._sub_lock = RLock()

    @override
    def open(self, *_, **__):
        auth_status = get_auth_status(self.request)
        if auth_status != AuthStatus.OK:
            self.close(code=1008, reason=auth_status.value.message)  # Policy Violation
            return

        logger.info(
            'Client %s connected to %s', self.request.remote_ip, self.request.path
        )
        self.name = f'ws:{self.app_name()}@{self.request.remote_ip}'
        self.start()

    @override
    def data_received(self, *_, **__):
        pass

    @override
    def on_message(self, *_, **__):
        pass

    @abstractclassmethod
    def app_name(cls) -> str:
        raise NotImplementedError()

    @classmethod
    def path(cls) -> str:
        return f'/ws/{cls.app_name()}'

    @property
    def auth_required(self):
        return True

    def subscribe(self, *topics: str) -> None:
        with self._sub_lock:
            for topic in topics:
                self._sub.subscribe(topic)
                self._redis_topics.add(topic)

    def unsubscribe(self, *topics: str) -> None:
        with self._sub_lock:
            for topic in topics:
                if topic in self._redis_topics:
                    self._sub.unsubscribe(topic)
                    self._redis_topics.remove(topic)

    def listen(self) -> Generator[Any, None, None]:
        try:
            for msg in self._sub.listen():
                if (
                    msg.get('type') != 'message'
                    and msg.get('channel').decode() not in self._redis_topics
                ):
                    continue

                yield msg.get('data')
        except RedisConnectionError:
            return

    def send(self, msg: Union[str, bytes, dict, list, tuple, set]) -> None:
        if isinstance(msg, (list, tuple, set)):
            msg = list(msg)
        if isinstance(msg, (list, dict)):
            msg = json.dumps(msg, cls=Message.Encoder)

        self._io_loop.asyncio_loop.call_soon_threadsafe(  # type: ignore
            self.write_message, msg
        )

    @override
    def run(self) -> None:
        super().run()
        for topic in self._redis_topics:
            self._sub.subscribe(topic)

    @override
    def on_close(self):
        topics = self._redis_topics.copy()
        for topic in topics:
            self.unsubscribe(topic)

        self._sub.close()
        logger.info(
            'Client %s disconnected from %s, reason=%s, message=%s',
            self.request.remote_ip,
            self.request.path,
            self.close_code,
            self.close_reason,
        )
