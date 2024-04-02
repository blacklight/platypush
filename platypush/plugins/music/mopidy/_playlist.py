from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from platypush.schemas.mopidy import MopidyPlaylistSchema

from ._track import MopidyTrack


@dataclass
class MopidyPlaylist:
    """
    Model for a Mopidy playlist.
    """

    uri: str
    name: str
    last_modified: Optional[datetime] = None
    tracks: List[MopidyTrack] = field(default_factory=list)
    type: str = "playlist"

    @classmethod
    def parse(cls, playlist: dict) -> "MopidyPlaylist":
        """
        Parse a Mopidy playlist from a dictionary received from the Mopidy API.
        """
        return cls(**MopidyPlaylistSchema().load(playlist))  # type: ignore

    def to_dict(self) -> dict:
        """
        Convert the Mopidy playlist to a dictionary.
        """
        return dict(MopidyPlaylistSchema().dump(self))
