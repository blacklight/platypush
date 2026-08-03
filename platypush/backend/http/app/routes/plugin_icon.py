import logging
import os
import pathlib
import re
import threading
import time
from collections import defaultdict
from io import BytesIO
from typing import Optional
from urllib.parse import urljoin

import requests
from flask import Blueprint, abort, make_response, request
from PIL import Image

from platypush.backend.http.app import template_folder
from platypush.config import Config

plugin_icon = Blueprint('plugin_icon', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    plugin_icon,
]

CACHE_TTL = 24 * 60 * 60  # 24 hours in seconds
CACHE_DIR_NAME = 'icons_cache'
CDN_BASE_URL = 'https://static.platypush.tech/icons/'
DEFAULT_ICON = os.path.join(template_folder, 'img', 'icons', 'logo-256x256.png')
LOCAL_ICONS_DIR = os.path.join(template_folder, 'icons')

# Plugin names may only contain letters, digits, dots, underscores and hyphens.
_plugin_name_re = re.compile(r'^[a-zA-Z0-9_.-]+$')

# Thread locks for concurrent cache access
cache_locks = defaultdict(threading.RLock)
lock_lock = threading.RLock()

logger = logging.getLogger(__name__)


def _get_cache_lock(name: str) -> threading.RLock:
    """Get or create a thread lock for a plugin name to prevent concurrent CDN fetches."""
    with lock_lock:
        return cache_locks[name]


def _get_cache_dir() -> str:
    """Get the server-side cache directory for plugin icons."""
    return os.path.join(Config.get_cachedir(), CACHE_DIR_NAME)


def get_cached_path(name: str) -> str:
    """Get the cache path for a plugin icon."""
    return os.path.join(_get_cache_dir(), f'{name}.png')


def is_cache_valid(cache_path: str) -> bool:
    """Check if a cached file exists and is not stale."""
    if not os.path.exists(cache_path):
        return False
    return (os.path.getmtime(cache_path) + CACHE_TTL) > time.time()


def clean_cache():
    """Clean up stale cache entries (older than 30 days)."""
    try:
        cache_dir = _get_cache_dir()
    except Exception:
        return

    if not os.path.isdir(cache_dir):
        return

    now = time.time()
    for filename in os.listdir(cache_dir):
        path = os.path.join(cache_dir, filename)
        if os.path.isfile(path) and os.path.getmtime(path) < (now - 30 * 24 * 60 * 60):
            try:
                os.unlink(path)
            except OSError:
                pass


def get_short_name(name: str) -> str:
    """Extract the short name from a dotted plugin name (e.g., 'media.jellyfin' -> 'jellyfin')."""
    return name.split('.')[-1]


def get_local_icon_path(name: str, base_dir: Optional[str] = None) -> Optional[str]:
    """Check for a local icon file in the configured icons directory."""
    short_name = get_short_name(name)
    local_dir = base_dir or LOCAL_ICONS_DIR

    # Check for SVG first
    svg_path = os.path.join(local_dir, f'{short_name}.svg')
    if os.path.exists(svg_path):
        return svg_path

    # Check for PNG
    png_path = os.path.join(local_dir, f'{short_name}.png')
    if os.path.exists(png_path):
        return png_path

    return None


def fetch_from_cdn(name: str, size: int = 256) -> Optional[bytes]:
    """Fetch an icon from the CDN."""
    url = urljoin(CDN_BASE_URL, f'{name}-{size}.png')
    try:
        response = requests.get(url, timeout=5)
    except requests.RequestException:
        return None

    if response.status_code == 200:
        return response.content

    # Fall back to the 64px variant if the requested size is not available
    if size != 64:
        return fetch_from_cdn(name, 64)

    return None


def resize_image(content: bytes, size: int) -> bytes:
    """Resize an image to the requested size using Pillow."""
    img = Image.open(BytesIO(content))

    # Only resize if needed
    if img.size != (size, size):
        try:
            resample = Image.Resampling.LANCZOS
        except AttributeError:
            resample = Image.LANCZOS  # type: ignore

        if img.mode in ('P', 'PA'):
            img = img.convert('RGBA')

        img = img.resize((size, size), resample)

    output = BytesIO()
    img.save(output, format='PNG')
    return output.getvalue()


def serve_svg(path: str, size: int):
    """Serve an SVG file with size attributes."""
    with open(path, 'r') as f:
        svg_content = f.read()

    # Inject width/height attributes if not present
    if not re.search(r'\bwidth\s*=', svg_content) and not re.search(
        r'\bheight\s*=', svg_content
    ):
        svg_content = re.sub(
            r'(<svg[^>]*)>',
            r'\1 width="{}" height="{}">'.format(size, size),
            svg_content,
            count=1,
        )

    response = make_response(svg_content)
    response.headers['Content-Type'] = 'image/svg+xml'
    response.headers['Cache-Control'] = f'public, max-age={CACHE_TTL}'
    return response


def serve_png(content: bytes, size: int):
    """Serve a PNG image, resized to the requested size."""
    resized = resize_image(content, size)
    response = make_response(resized)
    response.headers['Content-Type'] = 'image/png'
    response.headers['Cache-Control'] = f'public, max-age={CACHE_TTL}'
    return response


@plugin_icon.route('/plugin/<name>/icon', methods=['GET'])
def plugin_icon_route(name: str):
    """Serve a plugin icon with three-tier resolution: local -> CDN -> default."""
    if not _plugin_name_re.match(name):
        abort(404)

    try:
        size = int(request.args.get('size', 512))
    except (TypeError, ValueError):
        size = 512

    if size <= 0:
        size = 512

    # Ensure cache directory exists
    pathlib.Path(_get_cache_dir()).mkdir(parents=True, exist_ok=True)
    errors = []

    # 1. Check local filesystem
    try:
        local_path = get_local_icon_path(name)
        if local_path:
            if local_path.endswith('.svg'):
                return serve_svg(local_path, size)

            with open(local_path, 'rb') as f:
                content = f.read()
            return serve_png(content, size)
    except Exception as e:
        errors.append(e)

    # 2. Check server-side cache
    cache_path = get_cached_path(name)
    try:
        if is_cache_valid(cache_path):
            with open(cache_path, 'rb') as f:
                content = f.read()
            return serve_png(content, size)
    except Exception as e:
        errors.append(e)

    # 3. Fetch from CDN (with a thread lock to prevent concurrent fetches)
    try:
        lock = _get_cache_lock(name)
        with lock:
            # Double-check the cache in case another thread fetched it while we waited
            if is_cache_valid(cache_path):
                with open(cache_path, 'rb') as f:
                    content = f.read()
                return serve_png(content, size)

            content = fetch_from_cdn(name)
            if content:
                with open(cache_path, 'wb') as f:
                    f.write(content)
                return serve_png(content, size)
    except Exception as e:
        errors.append(e)

    # 4. Fallback to the default app icon
    try:
        with open(DEFAULT_ICON, 'rb') as f:
            content = f.read()
        return serve_png(content, size)
    except Exception as e:
        errors.append(e)

    # 5. Return a 404
    logger.warning('Failed to fetch plugin icon for %s: %s', name, errors)
    abort(404)


# Clean cache on startup
clean_cache()


# vim:sw=4:ts=4:et:
