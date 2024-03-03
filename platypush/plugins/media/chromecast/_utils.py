import datetime
from typing import Any, Callable, Optional

import pychromecast  # type: ignore

from platypush.context import get_bus
from platypush.message.event.media import MediaEvent

MediaCallback = Callable[[MediaEvent, pychromecast.Chromecast], Optional[Any]]


def convert_status(status) -> dict:
    """
    Convert a Chromecast status object to a dictionary.
    """
    attrs = [
        a
        for a in dir(status)
        if not a.startswith('_') and not callable(getattr(status, a))
    ]

    renamed_attrs = {
        'current_time': 'position',
        'player_state': 'state',
        'supports_seek': 'seekable',
        'volume_level': 'volume',
        'volume_muted': 'muted',
        'content_id': 'url',
    }

    ret = {}
    for attr in attrs:
        value = getattr(status, attr)
        if attr == 'volume_level':
            value = round(100 * value, 2)
        if attr == 'player_state':
            value = value.lower()
            if value == 'paused':
                value = 'pause'
            if value == 'playing':
                value = 'play'
        if isinstance(value, datetime.datetime):
            value = value.isoformat()

        if attr in renamed_attrs:
            ret[renamed_attrs[attr]] = value
        else:
            ret[attr] = value

    return ret


def post_event(
    evt_type,
    callback: Optional[MediaCallback] = None,
    chromecast: Optional[pychromecast.Chromecast] = None,
    **evt
):
    evt['plugin'] = 'media.chromecast'
    event = evt_type(player=evt.get('device'), **evt)

    get_bus().post(event)
    if callback:
        callback(event, chromecast)
