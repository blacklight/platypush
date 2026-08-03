from typing import Optional
from urllib.parse import urlparse

from flask import Blueprint, jsonify, request, send_from_directory

from platypush.backend.http.app import template_folder
from platypush.config import Config

pwa = Blueprint('pwa', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    pwa,
]

DEFAULT_ICONS = [
    {
        "src": "/img/icons/favicon-16x16.png",
        "sizes": "16x16",
        "type": "image/png",
    },
    {
        "src": "/img/icons/favicon-32x32.png",
        "sizes": "32x32",
        "type": "image/png",
    },
    {
        "src": "/img/icons/apple-touch-icon-60x60.png",
        "sizes": "60x60",
        "type": "image/png",
    },
    {
        "src": "/img/icons/apple-touch-icon-76x76.png",
        "sizes": "76x76",
        "type": "image/png",
    },
    {
        "src": "/img/icons/apple-touch-icon-120x120.png",
        "sizes": "120x120",
        "type": "image/png",
    },
    {
        "src": "/img/icons/msapplication-icon-144x144.png",
        "sizes": "144x144",
        "type": "image/png",
    },
    {
        "src": "/img/icons/mstile-150x150.png",
        "sizes": "150x150",
        "type": "image/png",
    },
    {
        "src": "/img/icons/apple-touch-icon-152x152.png",
        "sizes": "152x152",
        "type": "image/png",
    },
    {
        "src": "/img/icons/apple-touch-icon-180x180.png",
        "sizes": "180x180",
        "type": "image/png",
    },
    {
        "src": "/img/icons/android-chrome-192x192.png",
        "sizes": "192x192",
        "type": "image/png",
    },
    {
        "src": "/img/icons/android-chrome-maskable-192x192.png",
        "sizes": "192x192",
        "type": "image/png",
        "purpose": "maskable",
    },
    {
        "src": "/img/icons/logo-256x256.png",
        "sizes": "256x256",
        "type": "image/png",
    },
    {
        "src": "/img/icons/android-chrome-512x512.png",
        "sizes": "512x512",
        "type": "image/png",
    },
    {
        "src": "/img/icons/android-chrome-maskable-512x512.png",
        "sizes": "512x512",
        "type": "image/png",
        "purpose": "maskable",
    },
]


def _get_plugin(url: Optional[str] = None) -> Optional[str]:
    if not url:
        return None

    path = urlparse(url).path.lstrip('/').split('/')
    if len(path) > 1 and path[0] == 'plugin':
        return path[1]

    return None


def _get_short_name(name: str) -> str:
    """Extract the short name from a dotted plugin name (e.g., 'media.jellyfin' -> 'jellyfin')."""
    return name.split('.')[-1]


def _plugin_icons(plugin: str) -> list:
    """Build the icons array for a plugin PWA manifest."""
    return [
        {
            "src": f"/plugin/{plugin}/icon?size=192",
            "sizes": "192x192",
            "type": "image/png",
            "purpose": "any",
        },
        {
            "src": f"/plugin/{plugin}/icon?size=512",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "any",
        },
        {
            "src": f"/plugin/{plugin}/icon?size=512",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "maskable",
        },
        # Always include a default maskable icon as fallback
        {
            "src": "/img/icons/android-chrome-maskable-512x512.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "maskable",
        },
    ]


@pwa.route('/manifest.json', methods=['GET'])
def manifest_json():
    """Generated manifest file for the PWA"""

    device_id = Config.get_device_id()
    referer = request.headers.get('Referer')
    plugin = _get_plugin(referer)
    start_url = '/'
    name = f'Platypush @ {device_id}'
    short_name = device_id
    icons = DEFAULT_ICONS

    if plugin:
        start_url = f'/plugin/{plugin}'
        name = f'Platypush - {plugin}'
        short_name = _get_short_name(plugin)
        icons = _plugin_icons(plugin)

    return jsonify(
        {
            "name": name,
            "short_name": short_name,
            "icons": icons,
            "gcm_sender_id": "",
            "gcm_user_visible_only": True,
            "start_url": start_url,
            "permissions": ["gcm"],
            "orientation": "any",
            "display": "standalone",
            "theme_color": "#000000",
            "background_color": "#ffffff",
        }
    )


@pwa.route('/service-worker.js', methods=['GET'])
def service_worker_js():
    """URL that serves the service worker for the PWA"""
    return send_from_directory(template_folder, 'service-worker.js')


# vim:sw=4:ts=4:et:
