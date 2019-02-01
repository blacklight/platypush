from platypush.message.event import Event
from platypush.message.event.media import MediaEvent


class VideoEvent(MediaEvent):
    """ Base class for video events """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class VideoPlayEvent(VideoEvent):
    """
    Event triggered when a new video content is played
    """

    def __init__(self, video=None, *args, **kwargs):
        """
        :param video: File name or URI of the played video
        :type video: str
        """

        super().__init__(*args, video=video, **kwargs)


class VideoStopEvent(VideoEvent):
    """
    Event triggered when a video is stopped
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class VideoPauseEvent(VideoEvent):
    """
    Event triggered when a video playback is paused
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class NewPlayingVideoEvent(VideoEvent):
    """
    Event triggered when a video playback is paused
    """

    def __init__(self, video=None, *args, **kwargs):
        """
        :param video: File name or URI of the played video
        :type video: str
        """

        super().__init__(*args, video=video, **kwargs)


# vim:sw=4:ts=4:et:
