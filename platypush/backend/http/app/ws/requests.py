from threading import Thread, current_thread
from typing import Set
from typing_extensions import override

from platypush.backend.http.app.utils import send_message
from platypush.message.request import Request

from . import WSRoute, logger


class WSRequestsProxy(WSRoute):
    """
    Websocket event proxy mapped to ``/ws/requests``.
    """

    _max_concurrent_requests: int = 10
    """ Maximum number of concurrent requests allowed on the same connection. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._requests: Set[Thread] = set()

    @classmethod
    @override
    def app_name(cls) -> str:
        return 'requests'

    def _handle_request(self, request: Request):
        self._requests.add(current_thread())
        try:
            response = send_message(request, wait_for_response=True)
            self.send(str(response))
        finally:
            self._requests.remove(current_thread())

    def on_message(self, message):
        if len(self._requests) > self._max_concurrent_requests:
            logger.info('Too many concurrent requests on %s', self)
            return

        try:
            msg = Request.build(message)
            assert isinstance(msg, Request), f'Expected {Request}, got {type(msg)}'
        except Exception as e:
            logger.info('Could not build request from %s: %s', message, e)
            logger.exception(e)
            return

        Thread(target=self._handle_request, args=(msg,)).start()
