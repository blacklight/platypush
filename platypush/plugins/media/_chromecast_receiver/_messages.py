import json
import socket
import struct
from typing import Optional

from .proto.cast_channel_pb2 import CastMessage


def encode_message(
    msg: dict,
    source_id: str,
    destination_id: str,
    namespace: str,
) -> bytes:
    """
    Encode a JSON message as a length-prefixed CastMessage frame.
    """
    payload = json.dumps(msg, ensure_ascii=False).encode('utf-8')
    cast = CastMessage()
    cast.protocol_version = CastMessage.ProtocolVersion.CASTV2_1_0
    cast.source_id = source_id
    cast.destination_id = destination_id
    cast.namespace = namespace
    cast.payload_type = CastMessage.PayloadType.STRING
    cast.payload_utf8 = payload.decode('utf-8')

    data = cast.SerializeToString()
    return struct.pack('>I', len(data)) + data


def encode_binary_message(
    payload: bytes,
    source_id: str,
    destination_id: str,
    namespace: str,
) -> bytes:
    """
    Encode a binary message as a length-prefixed CastMessage frame.
    """
    cast = CastMessage()
    cast.protocol_version = CastMessage.ProtocolVersion.CASTV2_1_0
    cast.source_id = source_id
    cast.destination_id = destination_id
    cast.namespace = namespace
    cast.payload_type = CastMessage.PayloadType.BINARY
    cast.payload_binary = payload

    data = cast.SerializeToString()
    return struct.pack('>I', len(data)) + data


def decode_frame(data: bytes) -> CastMessage:
    """
    Decode a protobuf CastMessage from raw frame bytes.
    """
    cast = CastMessage()
    cast.ParseFromString(data)
    return cast


def read_message(sock: socket.socket) -> Optional[CastMessage]:
    """
    Read a single length-prefixed CastMessage from a socket.
    Returns ``None`` on EOF.
    """
    length_bytes = _recvall(sock, 4)
    if length_bytes is None:
        return None

    (length,) = struct.unpack('>I', length_bytes)
    if not length:
        return None

    payload = _recvall(sock, length)
    if payload is None:
        return None

    return decode_frame(payload)


def _recvall(sock: socket.socket, n: int) -> Optional[bytes]:
    """
    Receive exactly ``n`` bytes from a socket.
    """
    data = bytearray()
    while len(data) < n:
        try:
            chunk = sock.recv(n - len(data))
        except OSError:
            return None

        if not chunk:
            return None

        data.extend(chunk)

    return bytes(data)
