from dataclasses import dataclass
from typing import Optional

from platypush.schemas.mopidy import MopidyTrackSchema

from ._exc import EmptyTrackException


@dataclass
class MopidyTrack:
    """
    Model for a Mopidy track.
    """

    uri: str
    artist: Optional[str] = None
    title: Optional[str] = None
    album: Optional[str] = None
    artist_uri: Optional[str] = None
    album_uri: Optional[str] = None
    time: Optional[float] = None
    playlist_pos: Optional[int] = None
    track_id: Optional[int] = None
    track_no: Optional[int] = None
    date: Optional[str] = None
    genre: Optional[str] = None
    type: str = 'track'

    @classmethod
    def parse(cls, track: dict) -> Optional["MopidyTrack"]:
        """
        Parse a Mopidy track from a dictionary received from the Mopidy API.
        """
        try:
            return cls(**MopidyTrackSchema().load(track))  # type: ignore
        except EmptyTrackException:
            return None

    def to_dict(self) -> dict:
        """
        Convert the Mopidy track to a dictionary.
        """
        return dict(MopidyTrackSchema().dump(self))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MopidyTrack):
            return False

        return (
            self.uri == other.uri
            and self.artist == other.artist
            and self.title == other.title
            and self.album == other.album
            and self.time == other.time
        )
