from flask import Blueprint, jsonify, send_from_directory

from platypush.config import Config
from platypush.backend.http.app import template_folder

pwa = Blueprint('pwa', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    pwa,
]


@pwa.route('/manifest.json', methods=['GET'])
def manifest_json():
    """Generated manifest file for the PWA"""
    return jsonify(
        {
            "name": f'Platypush @ {Config.get("device_id")}',
            "short_name": Config.get('device_id'),
            "icons": [
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
            ],
            "gcm_sender_id": "",
            "gcm_user_visible_only": True,
            "start_url": "/",
            "permissions": ["gcm"],
            "orientation": "portrait",
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
