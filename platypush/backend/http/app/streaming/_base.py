from abc import ABC, abstractmethod
from http.client import responses
import json
from logging import getLogger
from typing import Optional
from typing_extensions import override

from tornado.web import RequestHandler, stream_request_body

from platypush.backend.http.app.utils.auth import AuthStatus, get_auth_status

from ..mixins import PubSubMixin

logger = getLogger(__name__)


@stream_request_body
class StreamingRoute(RequestHandler, PubSubMixin, ABC):
    """
    Base class for Tornado streaming routes.
    """

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

        logger.info(
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
