from platypush.message.event import Event


class TorrentEvent(Event):
    """
    Base class for torrent events
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TorrentDownloadStartEvent(TorrentEvent):
    """
    Event triggered upon torrent download start
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TorrentSeedingStartEvent(TorrentEvent):
    """
    Event triggered upon torrent seeding start
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TorrentDownloadProgressEvent(TorrentEvent):
    """
    Event triggered upon torrent download progress
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TorrentStateChangeEvent(TorrentEvent):
    """
    Event triggered upon torrent state change
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TorrentStateChangeEvent(TorrentEvent):
    """
    Event triggered upon torrent state change
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TorrentDownloadCompletedEvent(TorrentEvent):
    """
    Event triggered upon torrent state change
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TorrentDownloadStopEvent(TorrentEvent):
    """
    Event triggered when a torrent transfer is stopped
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# vim:sw=4:ts=4:et:

