from abc import ABC
from typing import Optional
from platypush.message.event import Event


class MediaEvent(Event):
    """Base class for media events"""

    def __init__(self, *args, player=None, plugin=None, status=None, **kwargs):
        super().__init__(*args, player=player, plugin=plugin, status=status, **kwargs)


class MediaPlayRequestEvent(MediaEvent):
    """
    Event triggered when a new media playback request is received
    """

    def __init__(
        self, player=None, plugin=None, resource=None, title=None, *args, **kwargs
    ):
        """
        :param resource: File name or URI of the played video
        :type resource: str
        """

        super().__init__(
            *args,
            player=player,
            plugin=plugin,
            resource=resource,
            title=title,
            **kwargs
        )


class MediaPlayEvent(MediaEvent):
    """
    Event triggered when a new media content is played
    """

    def __init__(
        self, player=None, plugin=None, resource=None, title=None, *args, **kwargs
    ):
        """
        :param resource: File name or URI of the played video
        :type resource: str
        """

        super().__init__(
            *args,
            player=player,
            plugin=plugin,
            resource=resource,
            title=title,
            **kwargs
        )


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
        super().__init__(
            *args, player=player, plugin=plugin, position=position, **kwargs
        )


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

        super().__init__(
            *args, player=player, plugin=plugin, resource=resource, **kwargs
        )


class MediaDownloadEvent(MediaEvent, ABC):
    """
    Base class for media download events.
    """

    def __init__(
        self,
        *args,
        plugin: str,
        resource: str,
        state: str,
        path: str,
        player: Optional[str] = None,
        size: Optional[int] = None,
        timeout: Optional[int] = None,
        progress: Optional[float] = None,
        started_at: Optional[float] = None,
        ended_at: Optional[float] = None,
        **kwargs
    ):
        """
        :param resource: File name or URI of the downloaded resource
        :param url: Alias for resource
        :param path: Path where the resource is downloaded
        :param state: Download state
        :param size: Size of the downloaded resource in bytes
        :param timeout: Download timeout in seconds
        :param progress: Download progress in percentage, between 0 and 100
        :param started_at: Download start time
        :param ended_at: Download end time
        """

        kwargs.update(
            {
                "resource": resource,
                "path": path,
                "url": resource,
                "state": state,
                "size": size,
                "timeout": timeout,
                "progress": progress,
                "started_at": started_at,
                "ended_at": ended_at,
            }
        )

        super().__init__(*args, player=player, plugin=plugin, **kwargs)


class MediaDownloadStartedEvent(MediaDownloadEvent):
    """
    Event triggered when a media download is started.
    """


class MediaDownloadProgressEvent(MediaDownloadEvent):
    """
    Event triggered when a media download is in progress.
    """


class MediaDownloadCompletedEvent(MediaDownloadEvent):
    """
    Event triggered when a media download is completed.
    """


class MediaDownloadErrorEvent(MediaDownloadEvent):
    """
    Event triggered when a media download fails.
    """

    def __init__(self, error: str, *args, **kwargs):
        """
        :param error: Error message.
        """
        super().__init__(*args, error=error, **kwargs)


class MediaDownloadPausedEvent(MediaDownloadEvent):
    """
    Event triggered when a media download is paused.
    """


class MediaDownloadResumedEvent(MediaDownloadEvent):
    """
    Event triggered when a media download is resumed.
    """


class MediaDownloadCancelledEvent(MediaDownloadEvent):
    """
    Event triggered when a media download is cancelled.
    """


class MediaDownloadClearEvent(MediaDownloadEvent):
    """
    Event triggered when a download is cleared from the queue.
    """


# vim:sw=4:ts=4:et:
