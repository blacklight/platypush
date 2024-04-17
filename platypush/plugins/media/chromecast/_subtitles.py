import logging

from pychromecast.controllers.media import MediaStatusListener


class SubtitlesAsyncHandler(MediaStatusListener):
    """
    This class is used to enable subtitles when the media is loaded.
    """

    def __init__(self, mc, subtitle_id):
        self.mc = mc
        self.subtitle_id = subtitle_id
        self.initialized = False
        self.logger = logging.getLogger(__name__)

    def new_media_status(self, *_):
        if self.subtitle_id and not self.initialized:
            self.mc.update_status()
            self.mc.enable_subtitle(self.subtitle_id)
            self.initialized = True

    def load_media_failed(self, queue_item_id: int, error_code: int) -> None:
        self.logger.warning(
            "Failed to load media with queue_item_id %d, error code: %d",
            queue_item_id,
            error_code,
        )
