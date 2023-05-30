from abc import ABC, abstractmethod
from logging import getLogger
from threading import Thread
from typing_extensions import override

from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler

from platypush.backend.http.app.utils.auth import AuthStatus, get_auth_status

from ..mixins import MessageType, PubSubMixin

logger = getLogger(__name__)


class WSRoute(WebSocketHandler, Thread, PubSubMixin, ABC):
    """
    Base class for Tornado websocket endpoints.
    """

    def __init__(self, *args, **kwargs):
        WebSocketHandler.__init__(self, *args)
        PubSubMixin.__init__(self, **kwargs)
        Thread.__init__(self)
        self._io_loop = IOLoop.current()

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
    def on_message(self, message):
        return message

    @classmethod
    @abstractmethod
    def app_name(cls) -> str:
        raise NotImplementedError()

    @classmethod
    def path(cls) -> str:
        return f'/ws/{cls.app_name()}'

    @property
    def auth_required(self):
        return True

    def send(self, msg: MessageType) -> None:
        self._io_loop.asyncio_loop.call_soon_threadsafe(  # type: ignore
            self.write_message, self._serialize(msg)
        )

    @override
    def run(self) -> None:
        super().run()
        self.subscribe(*self._subscriptions)

    @override
    def on_close(self):
        super().on_close()
        for channel in self._subscriptions.copy():
            self.unsubscribe(channel)

        if self._pubsub:
            self._pubsub.close()

        logger.info(
            'Client %s disconnected from %s, reason=%s, message=%s',
            self.request.remote_ip,
            self.request.path,
            self.close_code,
            self.close_reason,
        )
