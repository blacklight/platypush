from typing import Optional

from platypush.backend.http.app.utils import logger
from platypush.backend.http.media.handlers import MediaHandler

from ._registry import load_media_map, save_media_map, media_map_lock


def unregister_media(source: Optional[str] = None):
    """
    Unregisters a media streaming URL file given its source.
    """
    assert source is not None, 'No media_id specified'
    media_id = MediaHandler.get_media_id(source)
    media_info = {}

    with media_map_lock:
        media_map = load_media_map()
        if media_id not in media_map:
            raise FileNotFoundError(f'{source} is not a registered media_id')

        media_info = media_map.pop(media_id)
        save_media_map(media_map)

    logger().info('Unregistered %s from %s', source, media_info.url)
    return media_info
