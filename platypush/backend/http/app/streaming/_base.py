from abc import ABC, abstractmethod
from http.client import responses
import json
from logging import getLogger
from typing import Optional
from typing_extensions import override

from tornado.web import RequestHandler, stream_request_body

from platypush.backend.http.app.utils.auth import AuthStatus, get_auth_status

from ..mixins import PubSubMixin


@stream_request_body
class StreamingRoute(RequestHandler, PubSubMixin, ABC):
    """
    Base class for Tornado streaming routes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = getLogger(__name__)

    @override
    def prepare(self):
        """
        Request preparation logic. It performs user authentication if
        ``auth_required`` returns True, and it can be extended/overridden.
        """
        if self.auth_required:
            auth_status = get_auth_status(self.request)
            if auth_status != AuthStatus.OK:
                self.send_error(auth_status.value.code, error=auth_status.value.message)
                return

        self.logger.info(
            'Client %s connected to %s', self.request.remote_ip, self.request.path
        )

    @override
    def write_error(self, status_code: int, error: Optional[str] = None, **_):
        """
        Make sure that errors are always returned in JSON format.
        """
        self.set_header("Content-Type", "application/json")
        self.finish(
            json.dumps(
                {"status": status_code, "error": error or responses.get(status_code)}
            )
        )

    @classmethod
    @abstractmethod
    def path(cls) -> str:
        """
        Path/URL pattern for this route.
        """
        raise NotImplementedError()

    @property
    def auth_required(self) -> bool:
        """
        If set to True (default) then this route will require user
        authentication and return 401 if authentication fails.
        """
        return True

    @classmethod
    def _get_redis_queue(cls, *_, **__) -> Optional[str]:
        """
        Returns the Redis channel associated with a given set of arguments.

        This is None by default, and it should be implemented by subclasses if
        required.
        """
        return None

    def forward_stream(self, *args, **kwargs):
        """
        Utility method that does the following:

            1. It listens for new messages on the subscribed Redis channels;
            2. It applies a filter on the channel if :meth:`._get_redis_queue`
               returns a non-null result given ``args`` and ``kwargs``;
            3. It forward the frames read from the Redis channel(s) to the HTTP client;
            4. It periodically invokes :meth:`._should_stop` to cleanly
               terminate when the HTTP client socket is closed.

        """
        redis_queue = self._get_redis_queue(  # pylint: disable=assignment-from-none
            *args, **kwargs
        )

        if redis_queue:
            self.subscribe(redis_queue)

        try:
            for msg in self.listen():
                if self._should_stop():
                    break

                if redis_queue and msg.channel != redis_queue:
                    continue

                frame = msg.data
                if frame:
                    self.write(frame)
                    self.flush()
        finally:
            if redis_queue:
                self.unsubscribe(redis_queue)

    def _should_stop(self):
        """
        Utility method used by :meth:`._forward_stream` to automatically
        terminate when the client connection is closed (it can be overridden by
        the subclasses).
        """
        if self._finished:
            return True

        if self.request.connection and getattr(self.request.connection, 'stream', None):
            return self.request.connection.stream.closed()  # type: ignore

        return True
