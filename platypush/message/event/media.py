from platypush.message.event import Event


class MediaEvent(Event):
    """ Base class for media events """

    def __init__(self, player=None, plugin=None, *args, **kwargs):
        super().__init__(player=player, plugin=plugin, *args, **kwargs)


class MediaPlayRequestEvent(MediaEvent):
    """
    Event triggered when a new media playback request is received
    """

    def __init__(self, player=None, plugin=None, resource=None, title=None, *args, **kwargs):
        """
        :param resource: File name or URI of the played video
        :type resource: str
        """

        super().__init__(*args, player=player, plugin=plugin, resource=resource, title=title, **kwargs)


class MediaPlayEvent(MediaEvent):
    """
    Event triggered when a new media content is played
    """

    def __init__(self, player=None, plugin=None, resource=None, title=None, *args, **kwargs):
        """
        :param resource: File name or URI of the played video
        :type resource: str
        """

        super().__init__(*args, player=player, plugin=plugin, resource=resource, title=title, **kwargs)


class MediaStopEvent(MediaEvent):
    """
    Event triggered when a media is stopped
    """

    def __init__(self, player=None, plugin=None, *args, **kwargs):
        super().__init__(*args, player=player, plugin=plugin, **kwargs)


class MediaPauseEvent(MediaEvent):
    """
    Event triggered when a media playback is paused
    """

    def __init__(self, player=None, plugin=None, *args, **kwargs):
        super().__init__(*args, player=player, plugin=plugin, **kwargs)


class MediaResumeEvent(MediaEvent):
    """
    Event triggered when a media playback is resumed
    """

    def __init__(self, player=None, plugin=None, *args, **kwargs):
        super().__init__(*args, player=player, plugin=plugin, **kwargs)


class MediaSeekEvent(MediaEvent):
    """
    Event triggered when the time position in the media changes
    """

    def __init__(self, position, player=None, plugin=None, *args, **kwargs):
        super().__init__(*args, player=player, plugin=plugin, position=position, **kwargs)


class MediaVolumeChangedEvent(MediaEvent):
    """
    Event triggered when the media volume changes
    """

    def __init__(self, volume, player=None, plugin=None, *args, **kwargs):
        super().__init__(*args, player=player, plugin=plugin, volume=volume, **kwargs)


class MediaMuteChangedEvent(MediaEvent):
    """
    Event triggered when the media is muted/unmuted
    """

    def __init__(self, mute, player=None, plugin=None, *args, **kwargs):
        super().__init__(*args, player=player, plugin=plugin, mute=mute, **kwargs)


class NewPlayingMediaEvent(MediaEvent):
    """
    Event triggered when a new media source is being played
    """

    def __init__(self, player=None, plugin=None, resource=None, *args, **kwargs):
        """
        :param resource: File name or URI of the played resource
        :type resource: str
        """

        super().__init__(*args, player=player, plugin=plugin, resource=resource, **kwargs)


# vim:sw=4:ts=4:et:
