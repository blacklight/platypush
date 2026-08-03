from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from pychromecast import ChromecastConnectionError
from pychromecast.models import CastInfo, HostServiceInfo, MDNSServiceInfo

from platypush.plugins.media.chromecast import MediaChromecastPlugin


@pytest.fixture
def plugin():
    return MediaChromecastPlugin()


def _cast_info(
    *,
    model_name='Chromecast',
    manufacturer='Google Inc.',
    friendly_name='Living Room',
    services=None,
    host='192.168.1.2',
    port=8009,
    cast_type=None,
):
    return CastInfo(
        services=services
        or {MDNSServiceInfo('Chromecast-abc._googlecast._tcp.local.')},
        uuid=uuid4(),
        model_name=model_name,
        friendly_name=friendly_name,
        host=host,
        port=port,
        cast_type=cast_type,
        manufacturer=manufacturer,
    )


def test_is_local_receiver_by_model_name(plugin):
    info = _cast_info(
        model_name='Platypush',
        manufacturer='Platypush',
        friendly_name='Platypush Living Room',
    )
    assert plugin._is_local_receiver(info) is True


def test_is_local_receiver_by_service_name(plugin):
    info = _cast_info(
        model_name='Chromecast',
        manufacturer='Google Inc.',
        friendly_name='Platypush Living Room',
        services={MDNSServiceInfo('Platypush-abc123._googlecast._tcp.local.')},
    )
    assert plugin._is_local_receiver(info) is True


def test_is_local_receiver_real_device(plugin):
    info = _cast_info(
        model_name='Chromecast',
        manufacturer='Google Inc.',
        friendly_name='Living Room',
    )
    assert plugin._is_local_receiver(info) is False


def test_prepare_cast_info_skips_local(plugin):
    info = _cast_info(
        model_name='Platypush',
        manufacturer='Platypush',
        friendly_name='Platypush Living Room',
        services={MDNSServiceInfo('Platypush-abc123._googlecast._tcp.local.')},
    )
    assert plugin._prepare_cast_info(info) is None


def test_prepare_cast_info_skips_no_host(plugin):
    info = _cast_info(host=None, port=None)
    assert plugin._prepare_cast_info(info) is None


def test_prepare_cast_info_adds_host_service(plugin):
    info = _cast_info(
        services={MDNSServiceInfo('Chromecast-abc._googlecast._tcp.local.')},
        cast_type=None,
    )
    prepared = plugin._prepare_cast_info(info)
    assert prepared is not None
    assert HostServiceInfo('192.168.1.2', 8009) in prepared.services
    assert prepared is not info


def test_prepare_cast_info_reuses_existing_host_service(plugin):
    info = _cast_info(
        services={HostServiceInfo('192.168.1.2', 8009)},
        cast_type='cast',
    )
    prepared = plugin._prepare_cast_info(info)
    assert prepared is info


def test_get_chromecast_from_info_requires_host(plugin):
    info = _cast_info(host=None, port=None, services=set())
    with pytest.raises(ChromecastConnectionError):
        plugin._get_chromecast_from_info(info)


def test_refresh_chromecasts_skips_local_and_stale(plugin):
    local = _cast_info(
        model_name='Platypush',
        manufacturer='Platypush',
        friendly_name='Platypush Living Room',
        services={MDNSServiceInfo('Platypush-abc123._googlecast._tcp.local.')},
    )
    stale = _cast_info(friendly_name='Stale', host=None, port=None, services=set())
    real = _cast_info(friendly_name='Real')

    plugin._browser = MagicMock()
    plugin._browser.devices = {
        local.uuid: local,
        stale.uuid: stale,
        real.uuid: real,
    }
    plugin.browser.zc = MagicMock()

    mock_cc = MagicMock()
    mock_cc.uuid = real.uuid
    mock_cc.name = real.friendly_name
    mock_cc.socket_client = MagicMock(
        ident=1,
        is_alive=MagicMock(return_value=True),
        is_stopped=False,
    )

    with patch(
        'platypush.plugins.media.chromecast.get_chromecast_from_cast_info',
        return_value=mock_cc,
    ) as mock_get, patch(
        'platypush.plugins.media.chromecast.MediaListener', MagicMock()
    ):
        plugin._refresh_chromecasts()

    assert mock_get.call_count == 1
    called_info = mock_get.call_args[0][0]
    assert called_info.friendly_name == 'Real'
