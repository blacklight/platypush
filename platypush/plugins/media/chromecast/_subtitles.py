# pylint: disable=too-few-public-methods
class SubtitlesAsyncHandler:
    """
    This class is used to enable subtitles when the media is loaded.
    """

    def __init__(self, mc, subtitle_id):
        self.mc = mc
        self.subtitle_id = subtitle_id
        self.initialized = False

    def new_media_status(self, *_):
        if self.subtitle_id and not self.initialized:
            self.mc.update_status()
            self.mc.enable_subtitle(self.subtitle_id)
            self.initialized = True
