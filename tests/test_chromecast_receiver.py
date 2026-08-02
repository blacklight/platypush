import json
import os
from unittest.mock import patch

from platypush.plugins.media._chromecast_receiver._certificate import (
    load_or_create_certificate,
)
from platypush.plugins.media._chromecast_receiver._config import (
    ChromecastReceiverConfig,
)
from platypush.plugins.media._chromecast_receiver._media import resolve_media
from platypush.plugins.media._chromecast_receiver._messages import (
    decode_frame,
    encode_binary_message,
    encode_message,
)
from platypush.plugins.media._chromecast_receiver._state import (
    ChromecastReceiverState,
    PlayerState,
)
from platypush.plugins.media._chromecast_receiver._status import (
    build_media_status,
    build_receiver_status,
)
from platypush.plugins.media._chromecast_receiver.proto.cast_channel_pb2 import (
    DeviceAuthMessage,
)


class DummyMediaPlugin:
    """Minimal plugin stand-in for configuration and media tests."""


def test_encode_decode_roundtrip():
    payload = {'type': 'PING'}
    encoded = encode_message(payload, 'sender-0', 'receiver-0', 'ns')
    # encode_message returns length-prefixed frames; strip the prefix
    length = int.from_bytes(encoded[:4], 'big')
    assert length == len(encoded) - 4
    decoded = decode_frame(encoded[4:])
    assert decoded is not None
    assert json.loads(decoded.payload_utf8) == payload
    assert decoded.source_id == 'sender-0'
    assert decoded.destination_id == 'receiver-0'


def test_state_maps_player_status():
    state = ChromecastReceiverState()
    with patch('time.time', return_value=1000.0):
        assert state.update_player_state({'state': 'play'}) is True
        assert state.player_state == PlayerState.PLAYING

        assert state.update_player_state({'state': 'play'}) is False

        assert state.update_player_state(
            {'state': 'pause', 'position': 12.5, 'duration': 60}
        )
    assert state.player_state == PlayerState.PAUSED
    assert state.current_time == 12.5
    assert state.duration == 60


def test_set_media_clears_and_increments():
    state = ChromecastReceiverState()
    state.set_media(
        content_id='http://example.com/video.mp4',
        content_type='video/mp4',
        title='Test',
        stream_type='BUFFERED',
        subtitle_tracks=[],
        active_track_ids=[],
        current_time=10.0,
    )
    assert state.media_session_id == 1
    assert state.player_state == PlayerState.BUFFERING
    assert state.current_time == 10.0

    state.stop_media()
    assert state.player_state == PlayerState.IDLE
    assert state.media_session_id == 0

    state.set_media(
        content_id='http://example.com/audio.mp3',
        content_type='audio/mp3',
        title='Test 2',
        stream_type='BUFFERED',
        subtitle_tracks=[],
        active_track_ids=[],
    )
    assert state.media_session_id == 1


def test_build_media_status():
    state = ChromecastReceiverState()
    state.set_media(
        content_id='http://example.com/video.mp4',
        content_type='video/mp4',
        title='Test',
        stream_type='BUFFERED',
        subtitle_tracks=[],
        active_track_ids=[],
    )
    state.player_state = PlayerState.PLAYING
    status = build_media_status(state, 1)
    assert status['type'] == 'MEDIA_STATUS'
    assert status['requestId'] == 1
    assert len(status['status']) == 1
    media = status['status'][0]
    assert media['playerState'] == 'PLAYING'
    assert media['media']['contentId'] == 'http://example.com/video.mp4'
    assert media['mediaSessionId'] == 1


def test_build_receiver_status():
    state = ChromecastReceiverState()
    state.volume_level = 0.25
    status = build_receiver_status(state, 2)
    assert status['type'] == 'RECEIVER_STATUS'
    assert status['requestId'] == 2
    assert status['status']['applications'] == []
    assert status['status']['volume']['level'] == 0.25


def test_resolve_remote_media():
    resolved = resolve_media(
        plugin=DummyMediaPlugin(),
        media_base_url='http://localhost:8008',
        content_id='http://example.com/video.mp4',
        content_type='video/mp4',
        stream_type='BUFFERED',
        current_time=0,
        autoplay=True,
        tracks=[],
        metadata={'title': 'Remote Video'},
    )
    assert resolved['resolved_url'] == 'http://example.com/video.mp4'
    assert resolved['content_type'] == 'video/mp4'
    assert resolved['title'] == 'Remote Video'
    assert resolved['local'] is False


def test_config_defaults_and_device_id(tmp_path):
    with patch('platypush.config.Config.get_workdir', return_value=str(tmp_path)):
        cfg = ChromecastReceiverConfig.build(DummyMediaPlugin(), {'enabled': True})
    assert cfg.enabled is True
    assert cfg.port == 8009
    assert cfg.audio_only is False
    assert cfg.capabilities == 5
    assert len(cfg.allowed_networks) == 3


def test_certificate_generation(tmp_path):
    # Use an isolated workdir - never touch the certificate of a live instance
    with patch('platypush.config.Config.get_workdir', return_value=str(tmp_path)):
        cert, key = load_or_create_certificate('platypush-test')
        assert os.path.isfile(cert)
        assert os.path.isfile(key)
        with open(cert) as f:
            cert_data = f.read()
        with open(key) as f:
            key_data = f.read()
        assert 'BEGIN CERTIFICATE' in cert_data
        assert 'BEGIN PRIVATE KEY' in key_data or 'BEGIN RSA PRIVATE KEY' in key_data


def test_certificate_reuses_existing(tmp_path):
    with patch('platypush.config.Config.get_workdir', return_value=str(tmp_path)):
        cert1, key1 = load_or_create_certificate('platypush-test')
        mtime = os.path.getmtime(cert1)

        cert2, key2 = load_or_create_certificate('platypush-test')
        assert cert1 == cert2
        assert key1 == key2
        assert os.path.getmtime(cert2) == mtime


def test_encode_binary_roundtrip():
    challenge = DeviceAuthMessage()
    challenge.challenge.SetInParent()
    raw = challenge.SerializeToString()

    encoded = encode_binary_message(
        raw, 'sender-0', 'receiver-0', 'urn:x-cast:com.google.cast.tp.deviceauth'
    )
    length = int.from_bytes(encoded[:4], 'big')
    assert length == len(encoded) - 4

    decoded = decode_frame(encoded[4:])
    assert decoded.payload_type == decoded.BINARY
    assert decoded.namespace == 'urn:x-cast:com.google.cast.tp.deviceauth'

    parsed = DeviceAuthMessage()
    parsed.ParseFromString(decoded.payload_binary)
    assert parsed.HasField('challenge')


def test_device_auth_response(tmp_path):
    from platypush.plugins.media._chromecast_receiver._namespaces._deviceauth import (
        DeviceAuthNamespace,
    )

    # Generate a certificate in a temp directory first
    with patch('platypush.config.Config.get_workdir', return_value=str(tmp_path)):
        cert_path, key_path = load_or_create_certificate('test-device')

    with patch(
        'platypush.plugins.media._chromecast_receiver._namespaces._deviceauth.get_certificate_paths',
        return_value=(cert_path, key_path),
    ):
        handler = DeviceAuthNamespace(None, None)
        response_bytes = handler._build_response()

        response = DeviceAuthMessage()
        response.ParseFromString(response_bytes)
        assert response.HasField('response')
        assert len(response.response.signature) > 0
        assert len(response.response.client_auth_certificate) > 0

        # Verify the signature is valid
        from cryptography import x509
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding

        with open(cert_path, 'rb') as f:
            cert = x509.load_pem_x509_certificate(f.read())

        cert_der = cert.public_bytes(serialization.Encoding.DER)
        assert response.response.client_auth_certificate == cert_der

        # Verify signature using the public key
        public_key = cert.public_key()
        public_key.verify(
            response.response.signature, cert_der, padding.PKCS1v15(), hashes.SHA1()
        )
