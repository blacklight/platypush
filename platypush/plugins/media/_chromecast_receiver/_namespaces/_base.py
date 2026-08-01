import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class NamespaceHandler:
    """
    Base class for a Cast namespace handler.
    """

    namespace: str = ''

    def __init__(self, service, state):
        self.service = service
        self.state = state
        self.plugin = service.plugin
        self.config = service.config

    def can_handle(self, namespace: str) -> bool:
        return namespace == self.namespace

    def handle(
        self,
        session,
        message: Dict[str, Any],
        source_id: str,
        destination_id: str,
    ):
        """
        Dispatch a parsed JSON message to the appropriate handler method.
        """
        msg_type = message.get('type')
        handler = getattr(self, f'_handle_{msg_type}', None)
        if handler:
            handler(session, message, source_id, destination_id)
        else:
            logger.debug(
                'Unsupported message type for %s: %s', self.namespace, msg_type
            )

    def send(
        self,
        session,
        payload: Dict[str, Any],
        source_id: str,
        destination_id: str,
        namespace: Optional[str] = None,
    ):
        """
        Send a JSON payload on this namespace over a session.
        """
        namespace = namespace or self.namespace
        session.send_message(payload, source_id, destination_id, namespace)

    def broadcast(
        self,
        payload: Dict[str, Any],
        source_id: str,
        destination_id: str = '*',
        namespace: Optional[str] = None,
    ):
        """
        Broadcast a JSON payload to all connected sessions on this namespace.
        """
        namespace = namespace or self.namespace
        for session in list(self.service.sessions):
            try:
                session.send_message(payload, source_id, destination_id, namespace)
            except Exception as e:
                logger.warning('Could not broadcast to %s: %s', session, e)

    @staticmethod
    def request_id(message: Dict[str, Any]) -> int:
        return int(message.get('requestId', 0))
