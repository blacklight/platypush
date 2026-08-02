import logging
import os
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from platypush.utils import get_mime_type

from ._constants import STREAM_TYPE_BUFFERED, STREAM_TYPE_LIVE, STREAM_TYPE_NONE

logger = logging.getLogger(__name__)


def _is_local_resource(resource: str) -> bool:
    """
    Check whether a resource is a local file path or a ``file://`` URL.
    """
    parsed = urlparse(resource)
    if parsed.scheme == 'file':
        return True
    if parsed.scheme:
        return False
    return os.path.isfile(resource)


def _resolve_subtitle_url(
    tracks: List[dict],
    local: bool,
    source: str,
) -> Tuple[Optional[str], List[dict], List[int]]:
    """
    Pick the first supported text track and return its URL, the full track
    list and the active track IDs.
    """
    text_tracks = [
        t for t in tracks if t.get('type') == 'TEXT' or t.get('trackType') == 'TEXT'
    ]

    if not text_tracks:
        return None, [], []

    # Prefer WebVTT tracks
    text_tracks = sorted(
        text_tracks,
        key=lambda t: (
            t.get('trackContentType') != 'text/vtt' and t.get('subtype') != 'SUBTITLES'
        ),
    )

    chosen = text_tracks[0]
    track_id = int(chosen.get('trackId', 1))
    track_url = chosen.get('trackContentId')
    chosen['trackId'] = track_id

    if not track_url and local:
        # For local media with embedded subtitles, the sender may not provide a
        # URL; the player or streaming layer can extract them separately.
        track_url = source

    if local and track_url:
        # Absolute local paths must be passed as file:// or absolute path
        if track_url.startswith('file://'):
            track_url = track_url[len('file://') :]
        if os.path.isfile(track_url):
            track_url = os.path.abspath(track_url)

    for t in text_tracks:
        t.setdefault('type', 'TEXT')
        t.setdefault('subtype', 'SUBTITLES')

    return track_url, text_tracks, [track_id]


def _build_absolute_url(base_url: str, url: str) -> str:
    """
    Build an absolute URL from a base URL and a local path.
    """
    if url.startswith('http://') or url.startswith('https://'):
        return url

    if not url.startswith('/'):
        url = '/' + url

    return base_url.rstrip('/') + url


def resolve_media(
    plugin,
    media_base_url: str,
    content_id: str,
    content_type: Optional[str],
    stream_type: str,
    current_time: float,
    autoplay: bool,
    tracks: List[dict],
    metadata: Optional[dict] = None,
) -> Dict[str, Any]:
    """
    Resolve a Cast ``LOAD`` media payload to a playable URL and subtitle
    information for the underlying :class:`MediaPlugin`.

    Returns a dictionary with at least ``resolved_url``, ``content_type``,
    ``title``, ``subtitle_tracks`` and ``active_track_ids``.
    """
    source = content_id
    metadata = metadata or {}
    title = metadata.get('title')
    local = _is_local_resource(source)
    subtitle_url, subtitle_tracks, active_track_ids = _resolve_subtitle_url(
        tracks, local, source
    )

    if local:
        from platypush.backend.http.app.utils.routes import get_remote_base_url

        base_url = media_base_url or get_remote_base_url()
        resolved_url, content_type, stream_subtitles = _start_local_streaming(
            plugin, source, content_type, subtitle_url, base_url
        )
        if stream_subtitles:
            # Update the chosen track with the public VTT URL
            subtitle_tracks, active_track_ids = _update_subtitle_track_url(
                subtitle_tracks, active_track_ids, stream_subtitles
            )
    else:
        resolved_url = source

    if content_type:
        metadata['contentType'] = content_type

    try:
        mime_type = content_type if content_type else get_mime_type(resolved_url)
        content_type = content_type or mime_type
    except Exception as e:
        logger.debug('Could not infer MIME type for %s: %s', resolved_url, e)

    title = metadata.get('title')

    return {
        'resolved_url': resolved_url,
        'content_type': content_type or 'video/mp4',
        'stream_type': (
            stream_type
            if stream_type in (STREAM_TYPE_BUFFERED, STREAM_TYPE_LIVE, STREAM_TYPE_NONE)
            else STREAM_TYPE_BUFFERED
        ),
        'title': title,
        'subtitle_tracks': subtitle_tracks,
        'active_track_ids': active_track_ids,
        'current_time': current_time,
        'autoplay': autoplay,
        'local': local,
        'subtitle_url': subtitle_url,
    }


def _start_local_streaming(
    plugin,
    source: str,
    content_type: Optional[str],
    subtitle_url: Optional[str],
    media_base_url: str,
) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Start HTTP streaming for a local resource and return the public URL,
    content type and public subtitle URL.

    This relies on :meth:`MediaPlugin._start_streaming` (a private method)
    and on the ``url``, ``subtitles_url`` and ``mime_type`` keys in its
    return dictionary. Keep this in sync with ``MediaPlugin._start_streaming``.
    """
    result = plugin._start_streaming(source, subtitles=subtitle_url)
    resolved_url = _build_absolute_url(media_base_url, result.get('url', ''))
    if 'subtitles_url' in result:
        subtitles_url = _build_absolute_url(media_base_url, result['subtitles_url'])
    else:
        subtitles_url = None

    if not content_type:
        content_type = result.get('mime_type') or result.get('content_type')

    return resolved_url, content_type, subtitles_url


def _update_subtitle_track_url(
    subtitle_tracks: List[dict],
    active_track_ids: List[int],
    stream_subtitles: Optional[str],
) -> Tuple[List[dict], List[int]]:
    """
    Update the first text track with the public subtitle streaming URL.
    """
    if not stream_subtitles:
        return subtitle_tracks, active_track_ids

    if not subtitle_tracks:
        track_id = 1
        subtitle_tracks = [
            {
                'trackId': track_id,
                'type': 'TEXT',
                'trackContentId': stream_subtitles,
                'trackContentType': 'text/vtt',
                'subtype': 'SUBTITLES',
            }
        ]
        active_track_ids = [track_id]
    else:
        subtitle_tracks[0]['trackContentId'] = stream_subtitles
        subtitle_tracks[0]['trackContentType'] = 'text/vtt'

    return subtitle_tracks, active_track_ids
