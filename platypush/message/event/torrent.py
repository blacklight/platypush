from platypush.message.event import Event


class TorrentEvent(Event):
    """
    Base class for torrent events
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TorrentQueuedEvent(TorrentEvent):
    """
    Event triggered upon when a new torrent transfer is queued
    """
    def __init__(self, url, *args, **kwargs):
        super().__init__(*args, url=url, **kwargs)


class TorrentDownloadedMetadataEvent(TorrentEvent):
    """
    Event triggered upon torrent metadata download completed
    """
    def __init__(self, url, *args, **kwargs):
        super().__init__(*args, url=url, **kwargs)


class TorrentDownloadStartEvent(TorrentEvent):
    """
    Event triggered upon torrent download start
    """
    def __init__(self, url, *args, **kwargs):
        super().__init__(*args, url=url, **kwargs)


class TorrentSeedingStartEvent(TorrentEvent):
    """
    Event triggered upon torrent seeding start
    """
    def __init__(self, url, *args, **kwargs):
        super().__init__(*args, url=url, **kwargs)


class TorrentDownloadProgressEvent(TorrentEvent):
    """
    Event triggered upon torrent download progress
    """
    def __init__(self, url, *args, **kwargs):
        super().__init__(*args, url=url, **kwargs)


class TorrentStateChangeEvent(TorrentEvent):
    """
    Event triggered upon torrent state change
    """
    def __init__(self, url, *args, **kwargs):
        super().__init__(*args, url=url, **kwargs)


class TorrentPausedEvent(TorrentEvent):
    """
    Event triggered when a torrent transfer is paused
    """
    def __init__(self, url, *args, **kwargs):
        super().__init__(*args, url=url, **kwargs)


class TorrentResumedEvent(TorrentEvent):
    """
    Event triggered when a torrent transfer is resumed
    """
    def __init__(self, url, *args, **kwargs):
        super().__init__(*args, url=url, **kwargs)


class TorrentDownloadCompletedEvent(TorrentEvent):
    """
    Event triggered upon torrent state change
    """
    def __init__(self, url, *args, **kwargs):
        super().__init__(*args, url=url, **kwargs)


class TorrentDownloadStopEvent(TorrentEvent):
    """
    Event triggered when a torrent transfer is stopped
    """
    def __init__(self, url, *args, **kwargs):
        super().__init__(*args, url=url, **kwargs)


class TorrentRemovedEvent(TorrentEvent):
    """
    Event triggered when a torrent transfer is removed.
    """
    def __init__(self, url, *args, **kwargs):
        super().__init__(*args, url=url, **kwargs)


# vim:sw=4:ts=4:et:
