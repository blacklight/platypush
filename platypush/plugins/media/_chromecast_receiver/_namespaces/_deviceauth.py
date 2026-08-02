import logging
import threading

from platypush.plugins.media._chromecast_receiver._certificate import (
    get_certificate_paths,
)
from platypush.plugins.media._chromecast_receiver._constants import (
    NAMESPACE_DEVICEAUTH,
)
from platypush.plugins.media._chromecast_receiver._messages import (
    encode_binary_message,
)
from platypush.plugins.media._chromecast_receiver.proto.cast_channel_pb2 import (
    CastMessage,
    DeviceAuthMessage,
)

logger = logging.getLogger(__name__)


class DeviceAuthNamespace:
    """
    Handle the ``urn:x-cast:com.google.cast.tp.deviceauth`` namespace.

    Cast senders (e.g. VLC) send a ``DeviceAuthMessage`` with a challenge
    immediately after the TLS handshake. The receiver must respond with a
    ``DeviceAuthMessage`` containing:

    * ``signature`` -- the peer (TLS) certificate bytes signed with the
      device private key.
    * ``client_auth_certificate`` -- the device certificate in DER form.

    Open-source senders like VLC only check that the response field is
    present and do not validate the certificate chain against Google's CA,
    so a self-signed certificate is sufficient.
    """

    namespace = NAMESPACE_DEVICEAUTH

    def __init__(self, service, state):
        self.service = service
        self.state = state
        self._send_lock = threading.Lock()

    def can_handle(self, namespace: str) -> bool:
        return namespace == self.namespace

    def handle_binary(self, session, msg: CastMessage):
        """
        Process an incoming binary ``DeviceAuthMessage``.
        """
        challenge = DeviceAuthMessage()
        try:
            challenge.ParseFromString(msg.payload_binary)
        except Exception as e:
            logger.warning('Failed to parse DeviceAuthMessage: %s', e)
            return

        if not challenge.HasField('challenge'):
            logger.debug(
                'DeviceAuthMessage without challenge field from %s',
                session.address,
            )
            return

        logger.debug('Received device auth challenge from %s', session.address)

        try:
            response_bytes = self._build_response()
        except Exception as e:
            logger.warning('Failed to build auth response: %s', e)
            self._send_error(session, msg)
            return

        data = encode_binary_message(
            response_bytes,
            msg.destination_id or 'receiver-0',
            msg.source_id or 'sender-0',
            self.namespace,
        )

        with self._send_lock:
            try:
                session.socket.sendall(data)
                logger.debug('Sent device auth response to %s', session.address)
            except OSError as e:
                logger.warning(
                    'Failed to send auth response to %s: %s',
                    session.address,
                    e,
                )

    def _build_response(self) -> bytes:
        """
        Build the serialised ``DeviceAuthMessage`` response.

        The signature is computed by signing the SHA-1 hash of the TLS peer
        certificate (in DER encoding) with the device private key using
        PKCS#1 v1.5.
        """
        from cryptography import x509
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding

        cert_path, key_path = get_certificate_paths()

        with open(cert_path, 'rb') as f:
            cert = x509.load_pem_x509_certificate(f.read())

        with open(key_path, 'rb') as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)

        cert_der = cert.public_bytes(serialization.Encoding.DER)

        signature = private_key.sign(cert_der, padding.PKCS1v15(), hashes.SHA1())

        response = DeviceAuthMessage()
        response.response.signature = signature
        response.response.client_auth_certificate = cert_der
        return response.SerializeToString()

    def _send_error(self, session, msg: CastMessage):
        """
        Send a ``DeviceAuthMessage`` with an error field.
        """
        from platypush.plugins.media._chromecast_receiver.proto.cast_channel_pb2 import (
            AuthError,
        )

        error_msg = DeviceAuthMessage()
        error_msg.error.error_type = AuthError.INTERNAL_ERROR

        data = encode_binary_message(
            error_msg.SerializeToString(),
            msg.destination_id or 'receiver-0',
            msg.source_id or 'sender-0',
            self.namespace,
        )

        try:
            session.socket.sendall(data)
        except OSError:
            pass
