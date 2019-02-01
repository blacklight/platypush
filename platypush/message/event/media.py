from platypush.message.event import Event


class MediaEvent(Event):
    """ Base class for media events """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MediaPlayEvent(MediaEvent):
    """
    Event triggered when a new media content is played
    """

    def __init__(self, resource=None, *args, **kwargs):
        """
        :param resource: File name or URI of the played video
        :type resource: str
        """

        super().__init__(*args, resource=resource, **kwargs)


class MediaStopEvent(MediaEvent):
    """
    Event triggered when a media is stopped
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class MediaPauseEvent(MediaEvent):
    """
    Event triggered when a media playback is paused
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class NewPlayingMediaEvent(MediaEvent):
    """
    Event triggered when a new media source is being played
    """

    def __init__(self, resource=None, *args, **kwargs):
        """
        :param video: File name or URI of the played resource
        :type video: str
        """

        super().__init__(*args, resource=resource, **kwargs)


# vim:sw=4:ts=4:et:
