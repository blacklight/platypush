import logging

from platypush.plugins.media._chromecast_receiver._constants import NAMESPACE_CONNECTION

from ._base import NamespaceHandler

logger = logging.getLogger(__name__)


class ConnectionNamespace(NamespaceHandler):
    namespace = NAMESPACE_CONNECTION

    def _handle_CONNECT(self, session, message, source_id, destination_id):
        session.sender_id = source_id or 'sender-0'
        logger.debug('Sender connected: %s', session.sender_id)

    def _handle_CLOSE(self, session, message, source_id, destination_id):
        logger.debug('Sender requested close: %s', session.sender_id)
        session.close()
