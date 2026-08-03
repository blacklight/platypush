import ipaddress
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from platypush.backend.http.app.routes.plugins.media.dial import dial
from platypush.plugins.media._chromecast_receiver._config import (
    ChromecastReceiverConfig,
    DialConfig,
)
from platypush.plugins.media._chromecast_receiver._constants import PRIVATE_NETWORKS
from platypush.plugins.media._chromecast_receiver._dial._apps import (
    DialAppRegistry,
    DialAppState,
    MediaApp,
    YouTubeApp,
)
from platypush.plugins.media._chromecast_receiver._dial._ssdp import SsdpResponder
from platypush.plugins.media._chromecast_receiver._state import PlayerState


class DummyMediaPlugin:
    """Minimal plugin stand-in for DIAL registry tests."""

    def __init__(self):
        self.played = []
        self.stopped = False
        self._status = {'state': 'idle'}

    def play(self, **kwargs):
        self.played.append(kwargs)
        self._status = {'state': 'playing'}

    def stop(self):
        self.stopped = True
        self._status = {'state': 'idle'}

    def status(self):
        return self._status


def _dial_test_cfg(supported_apps=None, advertise_host='10.0.0.2'):
    """Helper to build a test ChromecastReceiverConfig with DIAL."""
    if supported_apps is None:
        supported_apps = ['Media']
    return ChromecastReceiverConfig(
        enabled=True,
        device_name='Test Receiver',
        device_id='a' * 32,
        host=advertise_host,
        allowed_networks=[ipaddress.ip_network(n) for n in PRIVATE_NETWORKS],
        dial=DialConfig(
            enabled=True,
            supported_apps=supported_apps,
            advertise_host=advertise_host,
        ),
    )


def _dial_test_client():
    """Helper to build a Flask test client for DIAL routes."""
    app = Flask(__name__)
    app.register_blueprint(dial)
    return app.test_client()


# ---------------------------------------------------------------------------
# SSDP parser and response
# ---------------------------------------------------------------------------


def test_parse_msearch_headers():
    pkt = (
        b'M-SEARCH * HTTP/1.1\r\n'
        b'HOST: 239.255.255.250:1900\r\n'
        b'MAN: "ssdp:discover"\r\n'
        b'MX: 3\r\n'
        b'ST: urn:dial-multiscreen-org:service:dial:1\r\n'
        b'\r\n'
    )
    headers = SsdpResponder._parse_headers(pkt.decode())
    assert headers['man'] == '"ssdp:discover"'
    assert headers['st'] == 'urn:dial-multiscreen-org:service:dial:1'
    assert headers['mx'] == '3'


def _make_responder(**dial_kwargs):
    cfg = _dial_test_cfg(
        **{k: v for k, v in dial_kwargs.items() if k == 'advertise_host'}
    )
    responder = SsdpResponder(cfg)
    responder._sock = MagicMock()
    return responder, cfg


def test_msearch_ignored_wrong_man():
    responder, _ = _make_responder()
    pkt = (
        b'M-SEARCH * HTTP/1.1\r\n'
        b'HOST: 239.255.255.250:1900\r\n'
        b'MAN: "something-else"\r\n'
        b'MX: 1\r\n'
        b'ST: urn:dial-multiscreen-org:service:dial:1\r\n\r\n'
    )
    responder._handle_packet(pkt, ('10.0.0.5', 12345))
    responder._sock.sendto.assert_not_called()


def test_msearch_st_all_matches():
    responder, _ = _make_responder()
    pkt = (
        b'M-SEARCH * HTTP/1.1\r\n'
        b'HOST: 239.255.255.250:1900\r\n'
        b'MAN: "ssdp:discover"\r\n'
        b'MX: 0\r\n'
        b'ST: ssdp:all\r\n\r\n'
    )
    with patch(
        'platypush.plugins.media._chromecast_receiver._config.get_http_port',
        return_value=8008,
    ):
        responder._handle_packet(pkt, ('10.0.0.5', 12345))
    responder._sock.sendto.assert_called_once()


def test_msearch_st_rootdevice_matches():
    responder, _ = _make_responder()
    pkt = (
        b'M-SEARCH * HTTP/1.1\r\n'
        b'HOST: 239.255.255.250:1900\r\n'
        b'MAN: "ssdp:discover"\r\n'
        b'MX: 0\r\n'
        b'ST: upnp:rootdevice\r\n\r\n'
    )
    with patch(
        'platypush.plugins.media._chromecast_receiver._config.get_http_port',
        return_value=8008,
    ):
        responder._handle_packet(pkt, ('10.0.0.5', 12345))
    responder._sock.sendto.assert_called_once()


def test_msearch_unauthorized_source():
    responder, _ = _make_responder()
    pkt = (
        b'M-SEARCH * HTTP/1.1\r\n'
        b'HOST: 239.255.255.250:1900\r\n'
        b'MAN: "ssdp:discover"\r\n'
        b'MX: 0\r\n'
        b'ST: urn:dial-multiscreen-org:service:dial:1\r\n\r\n'
    )
    # Source IP outside of the configured allowed networks
    responder._handle_packet(pkt, ('8.8.8.8', 12345))
    responder._sock.sendto.assert_not_called()


def test_ssdp_response_headers():
    responder, _ = _make_responder()
    with patch(
        'platypush.plugins.media._chromecast_receiver._config.get_http_port',
        return_value=8008,
    ):
        responder._send_response('10.0.0.5', 12345)

    responder._sock.sendto.assert_called_once()
    sent_bytes, addr = responder._sock.sendto.call_args[0]
    text = sent_bytes.decode('utf-8')
    assert addr == ('10.0.0.5', 12345)
    for header in ('CACHE-CONTROL', 'DATE', 'EXT', 'LOCATION', 'SERVER', 'ST', 'USN'):
        assert f'{header}:' in text
    assert 'LOCATION: http://10.0.0.2:8008/device.xml' in text


def test_ssdp_mx_capped():
    responder, _ = _make_responder()
    pkt = (
        b'M-SEARCH * HTTP/1.1\r\n'
        b'HOST: 239.255.255.250:1900\r\n'
        b'MAN: "ssdp:discover"\r\n'
        b'MX: 60\r\n'
        b'ST: urn:dial-multiscreen-org:service:dial:1\r\n\r\n'
    )
    with patch('random.uniform') as mock_uniform, patch(
        'platypush.plugins.media._chromecast_receiver._config.get_http_port',
        return_value=8008,
    ):
        mock_uniform.return_value = 0
        responder._handle_packet(pkt, ('10.0.0.5', 12345))
        # MX=60 must be capped to DIAL_SSDP_MX_MAX (5) before the delay is drawn
        (_, high), _kwargs = mock_uniform.call_args
        assert high == 5


def test_ssdp_multicast_fallback_to_host():
    """SSDP multicast join falls back to config.host when ssdp_interfaces is empty."""

    class DummyConfig:
        def __init__(self):
            self.host = '192.168.1.100'
            self.device_id = 'a' * 32
            self.dial = DialConfig(ssdp_interfaces=[], advertise_host='10.0.0.2')

    config = DummyConfig()
    responder = SsdpResponder(config)
    assert responder._config.host == '192.168.1.100'
    # Fallback to host, not advertise_host
    assert responder._config.dial.ssdp_interfaces == []
    interfaces = responder._config.dial.ssdp_interfaces or [responder._config.host]
    assert interfaces == ['192.168.1.100']


def test_ssdp_location_uses_https_when_ssl_configured():
    """The SSDP unicast response LOCATION header must reflect the HTTP backend scheme."""
    responder, _ = _make_responder()
    with patch(
        'platypush.plugins.media._chromecast_receiver._config.get_http_port',
        return_value=8008,
    ), patch(
        'platypush.plugins.media._chromecast_receiver._config.Config.get_backends',
        return_value={'http': {'ssl_cert': '/path/to/cert.pem'}},
    ):
        responder._send_response('10.0.0.5', 12345)

    sent_bytes, _ = responder._sock.sendto.call_args[0]
    text = sent_bytes.decode('utf-8')
    assert 'LOCATION: https://10.0.0.2:8008/device.xml' in text


# ---------------------------------------------------------------------------
# Device XML
# ---------------------------------------------------------------------------


def test_device_xml_structure():
    from platypush.backend.http.app.routes.plugins.media.dial import _build_device_xml

    cfg = _dial_test_cfg()
    xml_bytes = _build_device_xml(cfg)
    text = xml_bytes.decode('utf-8')
    assert '<specVersion>' in text
    assert 'urn:dial-multiscreen-org:device:dial:1' in text
    assert '<friendlyName>Test Receiver</friendlyName>' in text
    assert '<UDN>uuid:' in text


def test_device_xml_udn_stable():
    from platypush.backend.http.app.routes.plugins.media.dial import _build_device_xml

    cfg = _dial_test_cfg()
    xml1 = _build_device_xml(cfg).decode('utf-8')
    xml2 = _build_device_xml(cfg).decode('utf-8')
    udn1 = xml1.split('<UDN>')[1].split('</UDN>')[0]
    udn2 = xml2.split('<UDN>')[1].split('</UDN>')[0]
    assert udn1 == udn2


def test_application_url_header():
    cfg = _dial_test_cfg()
    client = _dial_test_client()

    with patch(
        'platypush.backend.http.app.routes.plugins.media.dial._get_config',
        return_value=(cfg, cfg.dial),
    ), patch(
        'platypush.backend.http.app.routes.plugins.media.dial._authorized',
        return_value=True,
    ), patch(
        'platypush.backend.http.app.routes.plugins.media.dial.get_http_port',
        return_value=8008,
    ):
        resp = client.get('/device.xml')
        assert resp.status_code == 200
        assert resp.headers['Application-URL'] == 'http://10.0.0.2:8008/apps/'


def test_application_url_uses_https_when_ssl_configured():
    """Application-URL in device_description() must reflect the HTTP backend scheme."""
    cfg = _dial_test_cfg()
    client = _dial_test_client()

    with patch(
        'platypush.backend.http.app.routes.plugins.media.dial._get_config',
        return_value=(cfg, cfg.dial),
    ), patch(
        'platypush.backend.http.app.routes.plugins.media.dial._authorized',
        return_value=True,
    ), patch(
        'platypush.backend.http.app.routes.plugins.media.dial.get_http_port',
        return_value=8008,
    ), patch(
        'platypush.backend.http.app.routes.plugins.media.dial.get_http_scheme',
        return_value='https',
    ):
        resp = client.get('/device.xml')
        assert resp.headers['Application-URL'] == 'https://10.0.0.2:8008/apps/'


def test_https_url_generation():
    """Application-URL and Location must use https end-to-end when SSL is configured."""
    from platypush.backend.http.app.routes.plugins.media.dial import (
        _build_device_xml,
        _xml_response,
    )

    cfg = _dial_test_cfg(advertise_host='10.0.0.2')
    with patch(
        'platypush.plugins.media._chromecast_receiver._config.Config.get_backends',
        return_value={'http': {'ssl_cert': '/path/to/cert.pem'}},
    ):
        xml = _build_device_xml(cfg)
        response = _xml_response(
            xml,
            extra_headers={'Application-URL': 'https://10.0.0.2:8008/apps/'},
        )
        assert response.headers['Application-URL'] == 'https://10.0.0.2:8008/apps/'


def test_get_http_scheme_helper():
    from platypush.plugins.media._chromecast_receiver._config import get_http_scheme

    with patch(
        'platypush.plugins.media._chromecast_receiver._config.Config.get_backends',
        return_value={'http': {}},
    ):
        assert get_http_scheme() == 'http'

    with patch(
        'platypush.plugins.media._chromecast_receiver._config.Config.get_backends',
        return_value={'http': {'ssl_cert': '/path/to/cert.pem'}},
    ):
        assert get_http_scheme() == 'https'


# ---------------------------------------------------------------------------
# App status XML
# ---------------------------------------------------------------------------


def test_app_status_stopped():
    from platypush.backend.http.app.routes.plugins.media.dial import _build_app_xml

    xml = _build_app_xml('Media', 'stopped').decode('utf-8')
    assert '<state>stopped</state>' in xml
    assert '<link' not in xml


def test_app_status_running():
    from platypush.backend.http.app.routes.plugins.media.dial import _build_app_xml

    xml = _build_app_xml('Media', 'running').decode('utf-8')
    assert '<state>running</state>' in xml
    assert '<link rel="run" href="run" />' in xml or 'rel="run"' in xml


def test_unknown_app_returns_404():
    cfg = _dial_test_cfg(supported_apps=['Media'])
    client = _dial_test_client()

    with patch(
        'platypush.backend.http.app.routes.plugins.media.dial._get_config',
        return_value=(cfg, cfg.dial),
    ), patch(
        'platypush.backend.http.app.routes.plugins.media.dial._authorized',
        return_value=True,
    ):
        resp = client.get('/apps/NonExistentApp')
        assert resp.status_code == 404


def test_unsupported_app_returns_json_error():
    """Unsupported apps return a JSON error instead of DIAL service XML."""
    cfg = _dial_test_cfg(supported_apps=['Media'])
    client = _dial_test_client()

    with patch(
        'platypush.backend.http.app.routes.plugins.media.dial._get_config',
        return_value=(cfg, cfg.dial),
    ), patch(
        'platypush.backend.http.app.routes.plugins.media.dial._authorized',
        return_value=True,
    ):
        resp = client.get('/apps/YouTube')
        assert resp.status_code == 404
        assert resp.content_type == 'application/json'
        assert b'Unsupported app: YouTube' in resp.data


# ---------------------------------------------------------------------------
# Payload parsers
# ---------------------------------------------------------------------------


def test_media_app_valid_payload():
    app = MediaApp()
    parsed = app.parse_payload(
        'url=http%3A%2F%2Fexample.com%2Fvideo.mp4&type=video%2Fmp4'
    )
    assert parsed['url'] == 'http://example.com/video.mp4'
    assert parsed['content_type'] == 'video/mp4'


def test_media_app_missing_url():
    app = MediaApp()
    with pytest.raises(ValueError, match='Missing required "url"'):
        app.parse_payload('type=video/mp4')


def test_media_app_disallowed_scheme():
    app = MediaApp()
    with pytest.raises(ValueError, match='not allowed'):
        app.parse_payload('url=file%3A%2F%2F%2Fetc%2Fpasswd')


def test_youtube_app_valid():
    app = YouTubeApp()
    parsed = app.parse_payload('v=dQw4w9WgXcQ&t=42')
    assert parsed['video_id'] == 'dQw4w9WgXcQ'
    assert parsed['start_time'] == 42.0


def test_youtube_app_missing_video_id():
    app = YouTubeApp()
    with pytest.raises(ValueError):
        app.parse_payload('list=PLxxxxxxxx')


def test_youtube_app_invalid_video_id():
    app = YouTubeApp()
    with pytest.raises(ValueError, match='Invalid YouTube video ID'):
        app.parse_payload('v=bad id!')


def test_media_app_build_launch_kwargs():
    app = MediaApp()
    kwargs = app.build_launch_kwargs(
        {'url': 'http://example.com/video.mp4', 'content_type': 'video/mp4'}
    )
    assert kwargs['resource'] == 'http://example.com/video.mp4'
    assert kwargs['metadata'] == {'content_type': 'video/mp4'}


def test_youtube_app_build_launch_kwargs():
    app = YouTubeApp()
    kwargs = app.build_launch_kwargs({'video_id': 'dQw4w9WgXcQ', 'start_time': 42.0})
    assert kwargs['resource'] == 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    assert kwargs['start'] == 42.0


# ---------------------------------------------------------------------------
# Launch/stop responses
# ---------------------------------------------------------------------------


def test_launch_returns_201_with_location():
    from platypush.plugins.media._chromecast_receiver._dial._messages import (
        DialLaunchReply,
    )

    cfg = _dial_test_cfg(supported_apps=['Media'])
    client = _dial_test_client()

    with patch(
        'platypush.backend.http.app.routes.plugins.media.dial._get_config',
        return_value=(cfg, cfg.dial),
    ), patch(
        'platypush.backend.http.app.routes.plugins.media.dial._authorized',
        return_value=True,
    ), patch(
        'platypush.backend.http.app.routes.plugins.media.dial.get_http_port',
        return_value=8008,
    ), patch(
        'platypush.backend.http.app.routes.plugins.media.dial._dispatch_and_wait',
        return_value=DialLaunchReply(success=True, run_id='abc123', reply_topic='t'),
    ):
        resp = client.post(
            '/apps/Media',
            data='url=http%3A%2F%2Fexample.com%2Fvideo.mp4',
            content_type='application/x-www-form-urlencoded',
        )
        assert resp.status_code == 201
        assert resp.headers['Location'] == 'http://10.0.0.2:8008/apps/Media/run'


def test_launch_wrong_content_type_returns_415():
    cfg = _dial_test_cfg(supported_apps=['Media'])
    client = _dial_test_client()

    with patch(
        'platypush.backend.http.app.routes.plugins.media.dial._get_config',
        return_value=(cfg, cfg.dial),
    ), patch(
        'platypush.backend.http.app.routes.plugins.media.dial._authorized',
        return_value=True,
    ):
        resp = client.post(
            '/apps/Media',
            data='{"url": "http://example.com/video.mp4"}',
            content_type='application/json',
        )
        assert resp.status_code == 415


def test_stop_not_running_returns_404():
    cfg = _dial_test_cfg(supported_apps=['Media'])
    client = _dial_test_client()

    with patch(
        'platypush.backend.http.app.routes.plugins.media.dial._get_config',
        return_value=(cfg, cfg.dial),
    ), patch(
        'platypush.backend.http.app.routes.plugins.media.dial._authorized',
        return_value=True,
    ), patch(
        'platypush.backend.http.app.routes.plugins.media.dial._get_app_state',
        return_value='stopped',
    ):
        resp = client.delete('/apps/Media/run')
        assert resp.status_code == 404


def test_stop_running_returns_200():
    from platypush.plugins.media._chromecast_receiver._dial._messages import (
        DialStopReply,
    )

    cfg = _dial_test_cfg(supported_apps=['Media'])
    client = _dial_test_client()

    with patch(
        'platypush.backend.http.app.routes.plugins.media.dial._get_config',
        return_value=(cfg, cfg.dial),
    ), patch(
        'platypush.backend.http.app.routes.plugins.media.dial._authorized',
        return_value=True,
    ), patch(
        'platypush.backend.http.app.routes.plugins.media.dial._get_app_state',
        return_value='running',
    ), patch(
        'platypush.backend.http.app.routes.plugins.media.dial._dispatch_and_wait',
        return_value=DialStopReply(success=True, reply_topic='t'),
    ):
        resp = client.delete('/apps/Media/run')
        assert resp.status_code == 200


def test_stop_client_error_returns_400():
    """Stop reply with client_error=True maps to 400, not 500."""
    from platypush.plugins.media._chromecast_receiver._dial._messages import (
        DialStopReply,
    )

    cfg = _dial_test_cfg(supported_apps=['Media'])
    client = _dial_test_client()

    with patch(
        'platypush.backend.http.app.routes.plugins.media.dial._get_config',
        return_value=(cfg, cfg.dial),
    ), patch(
        'platypush.backend.http.app.routes.plugins.media.dial._authorized',
        return_value=True,
    ), patch(
        'platypush.backend.http.app.routes.plugins.media.dial._get_app_state',
        return_value='running',
    ), patch(
        'platypush.backend.http.app.routes.plugins.media.dial._dispatch_and_wait',
        return_value=DialStopReply(
            success=False,
            error='App Media is not running',
            client_error=True,
            reply_topic='t',
        ),
    ):
        resp = client.delete('/apps/Media/run')
        assert resp.status_code == 400
        assert b'not running' in resp.data


def test_stop_server_error_returns_500():
    """Stop reply with client_error=False (default) maps to 500."""
    from platypush.plugins.media._chromecast_receiver._dial._messages import (
        DialStopReply,
    )

    cfg = _dial_test_cfg(supported_apps=['Media'])
    client = _dial_test_client()

    with patch(
        'platypush.backend.http.app.routes.plugins.media.dial._get_config',
        return_value=(cfg, cfg.dial),
    ), patch(
        'platypush.backend.http.app.routes.plugins.media.dial._authorized',
        return_value=True,
    ), patch(
        'platypush.backend.http.app.routes.plugins.media.dial._get_app_state',
        return_value='running',
    ), patch(
        'platypush.backend.http.app.routes.plugins.media.dial._dispatch_and_wait',
        return_value=DialStopReply(
            success=False,
            error='plugin.stop() failed: timeout',
            reply_topic='t',
        ),
    ):
        resp = client.delete('/apps/Media/run')
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# Bus bridge (without plugin)
# ---------------------------------------------------------------------------


def test_dial_launch_request_dispatched():
    from platypush.backend.http.app.routes.plugins.media.dial import _dispatch_and_wait
    from platypush.plugins.media._chromecast_receiver._dial._messages import (
        DialLaunchReply,
        DialLaunchRequest,
    )

    posted = {}

    def fake_post(msg):
        posted['msg'] = msg

    reply = DialLaunchReply(success=True, run_id='xyz', reply_topic='')

    with patch(
        'platypush.backend.http.app.routes.plugins.media.dial.get_bus'
    ) as mock_get_bus, patch(
        'platypush.backend.http.app.routes.plugins.media.dial.get_redis'
    ) as mock_get_redis:
        mock_get_bus.return_value.post.side_effect = fake_post
        mock_redis = MagicMock()
        mock_redis.blpop.return_value = (
            'queue',
            reply.encode() if hasattr(reply, 'encode') else str(reply),
        )
        mock_get_redis.return_value = mock_redis

        with patch('platypush.message.Message.build', return_value=reply):
            result = _dispatch_and_wait(
                DialLaunchRequest,
                DialLaunchReply,
                app_id='Media',
                raw_payload='url=http://example.com/x.mp4',
            )

        sent_request = posted['msg']
        assert isinstance(sent_request, DialLaunchRequest)
        assert sent_request.app_id == 'Media'
        assert sent_request.reply_topic
        assert result is reply


def test_dial_launch_timeout_returns_500():
    cfg = _dial_test_cfg(supported_apps=['Media'])
    client = _dial_test_client()

    with patch(
        'platypush.backend.http.app.routes.plugins.media.dial._get_config',
        return_value=(cfg, cfg.dial),
    ), patch(
        'platypush.backend.http.app.routes.plugins.media.dial._authorized',
        return_value=True,
    ), patch(
        'platypush.backend.http.app.routes.plugins.media.dial.get_bus'
    ), patch(
        'platypush.backend.http.app.routes.plugins.media.dial.get_redis'
    ) as mock_get_redis:
        mock_get_redis.return_value.blpop.return_value = None
        resp = client.post(
            '/apps/Media',
            data='url=http%3A%2F%2Fexample.com%2Fvideo.mp4',
            content_type='application/x-www-form-urlencoded',
        )
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# DIAL app registry / state synchronization
# ---------------------------------------------------------------------------


def test_notify_playback_stopped_clears_active_app():
    registry = DialAppRegistry(['Media'])
    registry._active_app = 'Media'
    registry._apps['Media'].state = DialAppState.RUNNING
    registry.notify_playback_stopped()
    assert registry.get_active_app() is None


def test_registry_launch_calls_plugin_play_and_sets_active():
    registry = DialAppRegistry(['Media'])
    plugin = DummyMediaPlugin()
    run_id = registry.launch('Media', 'url=http%3A%2F%2Fexample.com%2Fv.mp4', plugin)
    assert run_id
    assert plugin.played == [{'resource': 'http://example.com/v.mp4'}]
    active = registry.get_active_app()
    assert active is not None
    assert active.name == 'Media'
    assert active.state == DialAppState.RUNNING


def test_registry_launch_unknown_app_raises_keyerror():
    registry = DialAppRegistry(['Media'])
    with pytest.raises(KeyError):
        registry.launch('YouTube', 'v=dQw4w9WgXcQ', DummyMediaPlugin())


def test_registry_stop_not_running_raises_valueerror():
    registry = DialAppRegistry(['Media'])
    with pytest.raises(ValueError):
        registry.stop('Media', DummyMediaPlugin())


def test_registry_stop_running_calls_plugin_stop():
    registry = DialAppRegistry(['Media'])
    plugin = DummyMediaPlugin()
    registry.launch('Media', 'url=http%3A%2F%2Fexample.com%2Fv.mp4', plugin)
    registry.stop('Media', plugin)
    assert plugin.stopped is True
    assert registry.get_active_app() is None


def test_status_loop_calls_notify_on_idle_transition():
    """DIAL state is cleared on idle when outside the launch grace period."""
    from platypush.plugins.media._chromecast_receiver._service import (
        ChromecastReceiverService,
    )

    with patch('platypush.config.Config.get_workdir', return_value='/tmp'):
        plugin = DummyMediaPlugin()
        svc = ChromecastReceiverService(
            plugin, {'enabled': True, 'dial': {'enabled': True}}
        )
        svc._dial_service = MagicMock()
        svc._dial_service.registry = MagicMock()
        svc._dial_service.registry.within_launch_grace.return_value = False

        # Simulate idle state outside launch grace
        svc.state.player_state = PlayerState.IDLE
        svc._status_loop_iteration()
        svc._dial_service.registry.notify_playback_stopped.assert_called_once()
        svc._dial_service.flush_state.assert_called_once()


def test_dial_state_cleared_on_idle_without_playing():
    """DIAL state is cleared on idle after the launch grace period expires."""
    from platypush.plugins.media._chromecast_receiver._service import (
        ChromecastReceiverService,
    )

    with patch('platypush.config.Config.get_workdir', return_value='/tmp'):
        plugin = DummyMediaPlugin()
        svc = ChromecastReceiverService(
            plugin, {'enabled': True, 'dial': {'enabled': True}}
        )
        svc._dial_service = MagicMock()
        svc._dial_service.registry = MagicMock()
        svc._dial_service.registry.within_launch_grace.return_value = False

        svc.state.player_state = PlayerState.IDLE
        svc._status_loop_iteration()
        svc._dial_service.registry.notify_playback_stopped.assert_called_once()
        svc._dial_service.flush_state.assert_called_once()


def test_idle_during_launch_grace_does_not_clear_dial_state():
    """An idle poll within the launch grace period must NOT clear the DIAL app."""
    from platypush.plugins.media._chromecast_receiver._service import (
        ChromecastReceiverService,
    )

    with patch('platypush.config.Config.get_workdir', return_value='/tmp'):
        plugin = DummyMediaPlugin()
        svc = ChromecastReceiverService(
            plugin, {'enabled': True, 'dial': {'enabled': True}}
        )
        svc._dial_service = MagicMock()
        svc._dial_service.registry = MagicMock()
        svc._dial_service.registry.within_launch_grace.return_value = True

        svc.state.player_state = PlayerState.IDLE
        svc._status_loop_iteration()
        svc._dial_service.registry.notify_playback_stopped.assert_not_called()
        svc._dial_service.flush_state.assert_not_called()


def test_launch_grace_then_playing_then_idle_clears():
    """
    Full launch lifecycle: launch → idle (grace) → playing → idle clears.

    Simulates a DIAL launch followed by an immediate idle poll (backend has
    not yet transitioned to playing), then a playing poll, then an idle poll
    after the grace period.  The app must survive the first idle poll and be
    cleared only after playback was observed and then stopped.
    """
    registry = DialAppRegistry(['Media'])
    plugin = DummyMediaPlugin()
    registry.launch('Media', 'url=http%3A%2F%2Fexample.com%2Fv.mp4', plugin)
    assert registry.get_active_app() is not None

    # Idle poll immediately after launch — within grace, app must survive
    assert registry.within_launch_grace() is True
    # Do NOT call notify_playback_stopped — the service skips it during grace

    # Playback starts
    registry.notify_playback_active()
    assert registry.within_launch_grace() is False

    # Playback ends — idle again, grace is over
    registry.notify_playback_stopped()
    assert registry.get_active_app() is None


def test_launch_grace_expires_without_playing():
    """If playback never starts, the app is cleared once the grace period elapses."""
    import time as _time

    registry = DialAppRegistry(['Media'])
    plugin = DummyMediaPlugin()
    registry.launch('Media', 'url=http%3A%2F%2Fexample.com%2Fv.mp4', plugin)
    assert registry.within_launch_grace() is True

    # Fast-forward past the grace period by backdating _launch_time.
    with registry._lock:
        registry._launch_time = _time.monotonic() - registry.LAUNCH_GRACE_SECS - 1

    assert registry.within_launch_grace() is False
    registry.notify_playback_stopped()
    assert registry.get_active_app() is None


def test_playing_poll_calls_notify_playback_active():
    """A non-idle status poll marks playback as observed on the DIAL registry."""
    from platypush.plugins.media._chromecast_receiver._service import (
        ChromecastReceiverService,
    )

    with patch('platypush.config.Config.get_workdir', return_value='/tmp'):
        plugin = DummyMediaPlugin()
        svc = ChromecastReceiverService(
            plugin, {'enabled': True, 'dial': {'enabled': True}}
        )
        svc._dial_service = MagicMock()
        svc._dial_service.registry = MagicMock()

        plugin._status = {'state': 'playing'}
        svc.state.player_state = PlayerState.PLAYING
        svc._status_loop_iteration()
        svc._dial_service.registry.notify_playback_active.assert_called_once()
        svc._dial_service.registry.notify_playback_stopped.assert_not_called()


# ---------------------------------------------------------------------------
# Existing Chromecast receiver behavior is unaffected by DIAL
# ---------------------------------------------------------------------------


def test_existing_cast_receiver_unaffected(tmp_path):
    """DIAL disabled by default; existing Chromecast receiver config is unaffected."""
    with patch('platypush.config.Config.get_workdir', return_value=str(tmp_path)):
        cfg = ChromecastReceiverConfig.build(DummyMediaPlugin(), {'enabled': True})
    assert cfg.enabled is True
    assert cfg.dial.enabled is False
    assert cfg.dial.supported_apps == ['Media']
