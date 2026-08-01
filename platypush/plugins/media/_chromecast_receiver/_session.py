import json
import logging
import socket
import threading
import time
import uuid
from typing import Any, Dict, Optional

from ._constants import NAMESPACE_MEDIA, NAMESPACE_RECEIVER
from ._messages import encode_message, read_message
from ._namespaces import (
    ConnectionNamespace,
    HeartbeatNamespace,
    MediaNamespace,
    ReceiverNamespace,
)
from ._status import build_media_status, build_receiver_status
from .proto.cast_channel_pb2 import CastMessage

logger = logging.getLogger(__name__)


class CastSession(threading.Thread):
    """
    Per-sender Cast channel session.
    """

    def __init__(self, service, client_sock: socket.socket, address: tuple):
        super().__init__(name=f'CastSession-{address}', daemon=True)
        self.service = service
        self.config = service.config
        self.state = service.state
        self.plugin = service.plugin
        self.socket = client_sock
        self.address = address

        self.transport_id: Optional[str] = None
        self.sender_id: Optional[str] = None
        self.active_app_id: Optional[str] = None
        self.app_session_id: Optional[str] = None

        self.connected = False
        self.last_heartbeat = 0.0
        self.active_namespaces: set = set()
        self.alive = True
        self._send_lock = threading.Lock()

        self.handlers = [
            ConnectionNamespace(service, self.state),
            HeartbeatNamespace(service, self.state),
            ReceiverNamespace(service, self.state),
            MediaNamespace(service, self.state),
        ]

    def run(self):
        self.last_heartbeat = time.time()

        while self.alive and not self.service.should_stop.is_set():
            if HeartbeatNamespace.is_stale(self):
                logger.warning(
                    'Heartbeat timeout for %s; closing session', self.address
                )
                break

            try:
                msg = read_message(self.socket)
                if msg is None:
                    break

                if msg.payload_type != msg.STRING:
                    logger.warning(
                        'Received unsupported payload type %s from %s',
                        msg.payload_type,
                        self.address,
                    )
                    continue

                try:
                    payload = json.loads(msg.payload_utf8)
                except json.JSONDecodeError as e:
                    logger.warning(
                        'Malformed JSON payload from %s: %s', self.address, e
                    )
                    self._send_invalid_request(msg, payload=None)
                    continue

                self._handle_message(msg, payload)
            except OSError:
                break
            except Exception as e:
                logger.exception('Error handling Cast message: %s', e)
                break

        self.close()

    def _handle_message(
        self,
        msg: CastMessage,
        payload: Dict[str, Any],
    ):
        namespace = msg.namespace
        source_id = msg.source_id
        destination_id = msg.destination_id

        for handler in self.handlers:
            if handler.can_handle(namespace):
                handler.handle(self, payload, source_id, destination_id)
                return

        logger.debug('No handler for namespace %s from %s', namespace, self.address)

    def _send_invalid_request(self, msg: CastMessage, payload: Optional[dict]):
        request_id = 0
        if payload:
            try:
                request_id = int(payload.get('requestId', 0))
            except (TypeError, ValueError):
                pass

        try:
            self.send_message(
                {
                    'type': 'INVALID_REQUEST',
                    'requestId': request_id,
                    'reason': 'Invalid message',
                },
                msg.destination_id,
                msg.source_id,
                msg.namespace,
            )
        except Exception as e:
            logger.debug('Could not send INVALID_REQUEST: %s', e)

    def send_message(
        self,
        payload: Dict[str, Any],
        source_id: str,
        destination_id: str,
        namespace: str,
    ):
        with self._send_lock:
            if not self.alive:
                return

            try:
                data = encode_message(payload, source_id, destination_id, namespace)
                self.socket.sendall(data)
            except OSError as e:
                logger.debug('Could not send message to %s: %s', self.address, e)
                self.alive = False

    def launch_app(self, app_id: str, display_name: str):
        self.active_app_id = app_id
        self.app_session_id = uuid.uuid4().hex
        self.transport_id = f'transport-{uuid.uuid4().hex[:8]}'
        self.active_namespaces.add(NAMESPACE_MEDIA)
        self.state.set_application(
            app_id, display_name, self.app_session_id, self.transport_id
        )

    def stop_app(self):
        self.active_app_id = None
        self.app_session_id = None
        self.transport_id = None
        self.active_namespaces.discard(NAMESPACE_MEDIA)
        self.state.clear_application()

    def close(self):
        if not self.alive:
            return

        self.alive = False
        try:
            self.socket.close()
        except Exception as e:
            logger.debug('Error closing Cast session socket: %s', e)

        self.service.on_session_closed(self)

    def send_receiver_status(self, request_id: int = 0):
        if not self.alive:
            return
        # 'receiver-0' is the canonical Cast receiver endpoint ID.
        self.send_message(
            build_receiver_status(self.state, request_id),
            'receiver-0',
            self.sender_id or '*',
            NAMESPACE_RECEIVER,
        )

    def send_media_status(self, request_id: int = 0):
        if not self.alive or NAMESPACE_MEDIA not in self.active_namespaces:
            return
        self.send_message(
            build_media_status(self.state, request_id),
            self.transport_id or 'receiver-0',
            self.sender_id or '*',
            NAMESPACE_MEDIA,
        )
