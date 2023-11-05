from typing import Optional

from platypush.backend.http.app.utils import logger, send_request
from platypush.backend.http.media.handlers import MediaHandler

from ._registry import load_media_map, save_media_map


def get_media_url(media_id: str) -> str:
    """
    :returns: The URL of a media file given its ID
    """
    return f'/media/{media_id}'


def register_media(source: str, subtitles: Optional[str] = None) -> MediaHandler:
    """
    Registers a media file and returns its associated media handler.
    """
    media_id = MediaHandler.get_media_id(source)
    media_url = get_media_url(media_id)
    media_map = load_media_map()
    subfile = None

    if subtitles:
        req = {
            'type': 'request',
            'action': 'media.subtitles.download',
            'args': {
                'link': subtitles,
                'convert_to_vtt': True,
            },
        }

        try:
            subfile = (send_request(req) or {}).get('filename')
        except Exception as e:
            logger().warning('Unable to load subtitle %s: %s', subtitles, e)

    media_hndl = MediaHandler.build(source, url=media_url, subtitles=subfile)
    media_map[media_id] = media_hndl
    save_media_map(media_map)
    logger().info('Streaming "%s" on %s', source, media_url)
    return media_hndl
