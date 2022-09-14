from platypush.message.event import Event


class TidalEvent(Event):
    """Base class for Tidal events"""


class TidalPlaylistUpdatedEvent(TidalEvent):
    """
    Event fired when a Tidal playlist is updated.
    """

    def __init__(self, playlist_id: str, *args, **kwargs):
        super().__init__(*args, playlist_id=playlist_id, **kwargs)
