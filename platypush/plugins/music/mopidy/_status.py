from dataclasses import asdict, dataclass
from typing import Optional

from platypush.plugins.media import PlayerState
from platypush.schemas.mopidy import MopidyStatusSchema

from ._track import MopidyTrack


@dataclass
class MopidyStatus:
    """
    A dataclass to hold the status of the Mopidy client.
    """

    state: PlayerState = PlayerState.STOP
    volume: float = 0
    consume: bool = False
    random: bool = False
    repeat: bool = False
    single: bool = False
    mute: bool = False
    time: Optional[float] = None
    duration: Optional[float] = None
    playing_pos: Optional[int] = None
    track: Optional[MopidyTrack] = None

    def copy(self):
        return MopidyStatus(
            state=self.state,
            volume=self.volume,
            consume=self.consume,
            random=self.random,
            repeat=self.repeat,
            single=self.single,
            mute=self.mute,
            time=self.time,
            duration=self.duration,
            playing_pos=self.playing_pos,
            track=MopidyTrack(**asdict(self.track)) if self.track else None,
        )

    def to_dict(self):
        """
        Convert the Mopidy status to a dictionary.
        """
        return dict(MopidyStatusSchema().dump(self))
