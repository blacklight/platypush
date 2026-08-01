import logging
import time

from platypush.plugins.media._chromecast_receiver._constants import NAMESPACE_HEARTBEAT

from ._base import NamespaceHandler

logger = logging.getLogger(__name__)


class HeartbeatNamespace(NamespaceHandler):
    namespace = NAMESPACE_HEARTBEAT
    timeout = 30.0

    def _handle_PING(self, session, message, source_id, destination_id):
        session.send_message(
            {'type': 'PONG'},
            destination_id,
            source_id,
            NAMESPACE_HEARTBEAT,
        )

    def _handle_PONG(self, session, message, source_id, destination_id):
        session.last_heartbeat = time.time()

    @classmethod
    def is_stale(cls, session) -> bool:
        return (
            session.last_heartbeat > 0
            and time.time() - session.last_heartbeat > cls.timeout
        )
