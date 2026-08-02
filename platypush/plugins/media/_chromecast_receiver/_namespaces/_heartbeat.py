import logging
import time

from platypush.plugins.media._chromecast_receiver._constants import NAMESPACE_HEARTBEAT

from ._base import NamespaceHandler

logger = logging.getLogger(__name__)


class HeartbeatNamespace(NamespaceHandler):
    namespace = NAMESPACE_HEARTBEAT
    timeout = 30.0

    def _handle_PING(self, session, message, source_id, destination_id):
        # Update last_heartbeat when we receive a PING from the sender —
        # the Cast sender drives the heartbeat (it sends PINGs, we send PONGs).
        # Recording the receipt time here is what keeps the session alive.
        session.last_heartbeat = time.time()
        session.send_message(
            {'type': 'PONG'},
            destination_id,
            source_id,
            NAMESPACE_HEARTBEAT,
        )

    def _handle_PONG(self, session, message, source_id, destination_id):
        # Update last_heartbeat if the sender ever replies with a PONG too.
        session.last_heartbeat = time.time()

    @classmethod
    def is_stale(cls, session) -> bool:
        return (
            session.last_heartbeat > 0
            and time.time() - session.last_heartbeat > cls.timeout
        )
