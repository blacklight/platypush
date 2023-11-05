import json
import multiprocessing

from platypush.backend.http.app.utils import logger
from platypush.backend.http.media.handlers import MediaHandler
from platypush.message import Message
from platypush.utils import get_redis

from ._constants import MEDIA_MAP_VAR, MediaMap

media_map_lock = multiprocessing.RLock()


def load_media_map() -> MediaMap:
    """
    Load the media map from the server.
    """
    with media_map_lock:
        redis = get_redis()
        try:
            media_map = json.loads(
                ((redis.mget(MEDIA_MAP_VAR) or [None])[0] or b'{}').decode()  # type: ignore
            )
        except Exception as e:
            logger().warning('Could not load media map: %s', e)
            return {}

    return {
        media_id: MediaHandler.build(**media_info)
        for media_id, media_info in media_map.items()
    }


def save_media_map(new_map: MediaMap):
    """
    Updates the stored media map on the server.
    """
    with media_map_lock:
        redis = get_redis()
        redis.mset({MEDIA_MAP_VAR: json.dumps(new_map, cls=Message.Encoder)})
