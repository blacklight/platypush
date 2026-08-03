import json
from unittest.mock import patch

import pytest
from flask import Flask

from platypush.backend.http.app.routes.pwa import pwa


@pytest.fixture
def pwa_app():
    app = Flask(__name__)
    app.register_blueprint(pwa)
    with app.test_client() as client:
        yield client


def test_default_manifest(pwa_app):
    response = pwa_app.get('/manifest.json')
    assert response.status_code == 200
    manifest = json.loads(response.data)

    assert 'Platypush' in manifest['name']
    assert 'icons' in manifest
    assert len(manifest['icons']) == 14
    assert manifest['start_url'] == '/'


def test_plugin_manifest(pwa_app):
    with patch(
        'platypush.backend.http.app.routes.pwa._get_plugin',
        return_value='media.jellyfin',
    ):
        response = pwa_app.get(
            '/manifest.json',
            headers={'Referer': 'http://localhost/plugin/media.jellyfin'},
        )

    assert response.status_code == 200
    manifest = json.loads(response.data)

    assert manifest['name'] == 'Platypush - media.jellyfin'
    assert manifest['short_name'] == 'jellyfin'
    assert manifest['start_url'] == '/plugin/media.jellyfin'

    assert 'icons' in manifest
    assert len(manifest['icons']) == 4

    dynamic_icons = [
        icon
        for icon in manifest['icons']
        if '/plugin/media.jellyfin/icon' in icon['src']
    ]
    assert len(dynamic_icons) == 3

    sizes = {icon['sizes'] for icon in dynamic_icons}
    assert sizes == {'192x192', '512x512'}

    purposes = {icon.get('purpose', 'any') for icon in dynamic_icons}
    assert purposes == {'any', 'maskable'}

    # The last icon is always the default maskable fallback
    assert manifest['icons'][-1]['src'] == (
        '/img/icons/android-chrome-maskable-512x512.png'
    )
    assert manifest['icons'][-1]['purpose'] == 'maskable'


# vim:sw=4:ts=4:et:
