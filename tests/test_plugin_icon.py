from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask
from PIL import Image

from platypush.backend.http.app.routes import plugin_icon as plugin_icon_module


def _make_png(size, color='green'):
    """Create a PNG image in memory and return its bytes."""
    img = Image.new('RGB', (size, size), color=color)
    buf = BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()


def _make_test_icons(tmp_path):
    """Create a temporary set of local and default icons."""
    icons_dir = tmp_path / 'icons'
    icons_dir.mkdir()

    # SVG icon
    svg_path = icons_dir / 'test.svg'
    svg_path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
        '<circle cx="50" cy="50" r="40" fill="red"/></svg>'
    )

    # PNG icon
    png_path = icons_dir / 'test.png'
    img = Image.new('RGB', (256, 256), color='red')
    img.save(str(png_path))

    # A PNG-only plugin icon
    png_only_path = icons_dir / 'pngonly.png'
    img.save(str(png_only_path))

    # Default app icon
    default_dir = tmp_path / 'img' / 'icons'
    default_dir.mkdir(parents=True)
    default_img = Image.new('RGB', (256, 256), color='blue')
    default_img.save(str(default_dir / 'logo-256x256.png'))

    return icons_dir, default_dir


@pytest.fixture
def plugin_icon_setup(tmp_path, monkeypatch):
    icons_dir, default_dir = _make_test_icons(tmp_path)
    cache_dir = tmp_path / 'cache'
    cache_dir.mkdir()

    monkeypatch.setattr(plugin_icon_module, 'LOCAL_ICONS_DIR', str(icons_dir))
    monkeypatch.setattr(
        plugin_icon_module,
        'DEFAULT_ICON',
        str(default_dir / 'logo-256x256.png'),
    )
    monkeypatch.setattr(plugin_icon_module, '_get_cache_dir', lambda: str(cache_dir))

    app = Flask(__name__)
    app.register_blueprint(plugin_icon_module.plugin_icon)

    with app.test_client() as client:
        yield client


def test_get_short_name():
    assert plugin_icon_module.get_short_name('media.jellyfin') == 'jellyfin'
    assert plugin_icon_module.get_short_name('camera.ir.mlx90640') == 'mlx90640'


def test_get_local_icon_path(tmp_path):
    icons_dir, _ = _make_test_icons(tmp_path)

    # SVG takes precedence
    assert plugin_icon_module.get_local_icon_path(
        'test', base_dir=str(icons_dir)
    ) == str(icons_dir / 'test.svg')

    # PNG only
    assert plugin_icon_module.get_local_icon_path(
        'pngonly', base_dir=str(icons_dir)
    ) == str(icons_dir / 'pngonly.png')

    # Missing icon
    assert (
        plugin_icon_module.get_local_icon_path('nonexistent', base_dir=str(icons_dir))
        is None
    )


def test_fetch_from_cdn_success():
    with patch.object(plugin_icon_module.requests, 'get') as mock_get:
        mock_get.return_value = MagicMock(status_code=200, content=b'test_content')
        content = plugin_icon_module.fetch_from_cdn('test-plugin')

    assert content == b'test_content'
    mock_get.assert_called_once_with(
        'https://static.platypush.tech/icons/test-plugin-256.png', timeout=5
    )


def test_fetch_from_cdn_404_fallback():
    with patch.object(plugin_icon_module.requests, 'get') as mock_get:
        mock_get.side_effect = [
            MagicMock(status_code=404),
            MagicMock(status_code=200, content=b'test_content_64'),
        ]
        content = plugin_icon_module.fetch_from_cdn('test-plugin')

    assert content == b'test_content_64'
    assert mock_get.call_count == 2
    assert mock_get.call_args == (
        ('https://static.platypush.tech/icons/test-plugin-64.png',),
        {'timeout': 5},
    )


def test_fetch_from_cdn_request_exception():
    with patch.object(
        plugin_icon_module.requests,
        'get',
        side_effect=plugin_icon_module.requests.ConnectionError('boom'),
    ):
        assert plugin_icon_module.fetch_from_cdn('test-plugin') is None


def test_resize_image():
    img = Image.new('RGB', (256, 256), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()

    resized = plugin_icon_module.resize_image(img_bytes, 128)
    resized_img = Image.open(BytesIO(resized))
    assert resized_img.size == (128, 128)

    resized = plugin_icon_module.resize_image(img_bytes, 512)
    resized_img = Image.open(BytesIO(resized))
    assert resized_img.size == (512, 512)


def test_serve_svg(tmp_path):
    icons_dir, _ = _make_test_icons(tmp_path)
    svg_path = icons_dir / 'test.svg'

    app = Flask(__name__)
    with app.app_context():
        response = plugin_icon_module.serve_svg(str(svg_path), 64)

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'image/svg+xml'
    assert 'width="64" height="64"' in response.get_data(as_text=True)


def test_plugin_icon_local_svg(plugin_icon_setup):
    response = plugin_icon_setup.get('/plugin/test/icon?size=64')
    assert response.status_code == 200
    assert response.headers['Content-Type'].startswith('image/svg+xml')
    assert b'width="64" height="64"' in response.data


def test_plugin_icon_local_png(plugin_icon_setup):
    response = plugin_icon_setup.get('/plugin/pngonly/icon?size=128')
    assert response.status_code == 200
    assert response.headers['Content-Type'].startswith('image/png')

    img = Image.open(BytesIO(response.data))
    assert img.size == (128, 128)


def test_plugin_icon_cdn(plugin_icon_setup):
    png_bytes = _make_png(64, color='green')
    with patch.object(plugin_icon_module, 'fetch_from_cdn', return_value=png_bytes):
        response = plugin_icon_setup.get('/plugin/cdn-test/icon?size=64')

    assert response.status_code == 200
    assert response.headers['Content-Type'].startswith('image/png')
    assert response.data == png_bytes


def test_plugin_icon_default_fallback(plugin_icon_setup):
    with patch.object(plugin_icon_module, 'fetch_from_cdn', return_value=None):
        response = plugin_icon_setup.get('/plugin/unknown/icon?size=64')

    assert response.status_code == 200
    assert response.headers['Content-Type'].startswith('image/png')

    img = Image.open(BytesIO(response.data))
    assert img.size == (64, 64)


def test_plugin_icon_caches_cdn_result(plugin_icon_setup):
    cache_dir = Path(plugin_icon_module._get_cache_dir())
    assert cache_dir.is_dir()

    png_bytes = _make_png(64, color='yellow')
    with patch.object(
        plugin_icon_module, 'fetch_from_cdn', return_value=png_bytes
    ) as mock_fetch:
        response = plugin_icon_setup.get('/plugin/cache-test/icon?size=64')

    assert response.status_code == 200
    assert response.data == png_bytes
    assert mock_fetch.call_count == 1
    assert (cache_dir / 'cache-test.png').exists()

    # Second request should be served from cache without hitting the CDN
    with patch.object(
        plugin_icon_module, 'fetch_from_cdn', return_value=b'new_content'
    ) as mock_fetch:
        response = plugin_icon_setup.get('/plugin/cache-test/icon?size=64')

    assert response.status_code == 200
    assert response.data == png_bytes
    assert mock_fetch.call_count == 0


def test_plugin_icon_invalid_name(plugin_icon_setup):
    response = plugin_icon_setup.get('/plugin/bad%20name/icon')
    assert response.status_code == 404


# vim:sw=4:ts=4:et:
