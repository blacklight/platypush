import logging
import time
from typing import Optional

from platypush.message.event.media import (
    MediaPlayEvent,
    MediaStopEvent,
    MediaPauseEvent,
    NewPlayingMediaEvent,
    MediaVolumeChangedEvent,
    MediaSeekEvent,
)

from ._utils import MediaCallback, convert_status, post_event

logger = logging.getLogger(__name__)


class MediaListener:
    """
    Listens for media status changes and posts events accordingly.
    """

    def __init__(self, name: str, cast, callback: Optional[MediaCallback] = None):
        self.name = name
        self.cast = cast
        self.status = convert_status(cast.media_controller.status)
        self.last_status_timestamp = time.time()
        self.callback = callback

    def new_media_status(self, status):
        status = convert_status(status)
        if status.get('url') and status.get('url') != self.status.get('url'):
            self._post_event(
                NewPlayingMediaEvent,
                title=status.get('title'),
            )

        state = status.get('state')
        if state != self.status.get('state'):
            if state == 'play':
                self._post_event(MediaPlayEvent)
            elif state == 'pause':
                self._post_event(MediaPauseEvent)
            elif state in ('stop', 'idle'):
                self._post_event(MediaStopEvent)

        if status.get('volume') != self.status.get('volume'):
            self._post_event(MediaVolumeChangedEvent, volume=status.get('volume'))

        if (
            status.get('position')
            and self.status.get('position')
            and abs(status['position'] - self.status['position'])
            > time.time() - self.last_status_timestamp + 5
        ):
            self._post_event(MediaSeekEvent, position=status.get('position'))

        self.status = status
        self.last_status_timestamp = time.time()

    def load_media_failed(self, item, error_code):
        logger.warning('Failed to load media %s: %d', item, error_code)

    def _post_event(self, evt_type, **evt):
        status = evt.get('status', {})
        resource = status.get('url')
        args = {
            'device': self.name,
            'plugin': 'media.chromecast',
            **evt,
        }

        if resource:
            args['resource'] = resource

        post_event(evt_type, callback=self.callback, chromecast=self.cast, **args)
