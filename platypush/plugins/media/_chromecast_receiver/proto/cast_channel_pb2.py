# -*- coding: utf-8 -*-
# flake8: noqa
# Minimal protobuf definitions for the Chromecast cast-channel protocol.
#
# The serialized FileDescriptorProto uses the name
# ``platypush_cast_channel.proto`` (not ``cast_channel.proto``) so that this
# module can coexist with pychromecast's own generated ``cast_channel_pb2``
# without triggering a "duplicate file name" error in the global descriptor
# pool.
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_sym_db = _symbol_database.Default()

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x1cplatypush_cast_channel.proto"\xab\x02\n\x0bCastMessage\x126\n\x10protocol_version\x18\x01 \x02(\x0e2\x1c.CastMessage.ProtocolVersion\x12\x11\n\tsource_id\x18\x02 \x02(\t\x12\x16\n\x0edestination_id\x18\x03 \x02(\t\x12\x11\n\tnamespace\x18\x04 \x02(\t\x12.\n\x0cpayload_type\x18\x05 \x02(\x0e2\x18.CastMessage.PayloadType\x12\x14\n\x0cpayload_utf8\x18\x06 \x01(\t\x12\x16\n\x0epayload_binary\x18\x07 \x01(\x0c"!\n\x0fProtocolVersion\x12\x0e\n\nCASTV2_1_0\x10\x00"%\n\x0bPayloadType\x12\n\n\x06STRING\x10\x00\x12\n\n\x06BINARY\x10\x01"\x0f\n\rAuthChallenge"B\n\x0cAuthResponse\x12\x11\n\tsignature\x18\x01 \x02(\x0c\x12\x1f\n\x17client_auth_certificate\x18\x02 \x02(\x0c"b\n\tAuthError\x12(\n\nerror_type\x18\x01 \x02(\x0e2\x14.AuthError.ErrorType"+\n\tErrorType\x12\x12\n\x0eINTERNAL_ERROR\x10\x00\x12\n\n\x06NO_TLS\x10\x01"r\n\x11DeviceAuthMessage\x12!\n\tchallenge\x18\x01 \x01(\x0b2\x0e.AuthChallenge\x12\x1f\n\x08response\x18\x02 \x01(\x0b2\r.AuthResponse\x12\x19\n\x05error\x18\x03 \x01(\x0b2\n.AuthErrorB\x02H\x03'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(
    DESCRIPTOR, 'platypush_cast_channel_pb2', _globals
)
if not _descriptor._USE_C_DESCRIPTORS:
    _globals['DESCRIPTOR']._loaded_options = None
    _globals['DESCRIPTOR']._serialized_options = b'H\003'
