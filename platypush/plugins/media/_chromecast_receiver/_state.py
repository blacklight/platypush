import enum
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ._constants import (
    RECEIVER_STATUS_IDLE,
    RECEIVER_STATUS_PAUSED,
    RECEIVER_STATUS_PLAYING,
)


class ReceiverState(enum.Enum):
    IDLE = 'IDLE'
    LAUNCHED = 'LAUNCHED'


class PlayerState(enum.Enum):
    IDLE = 'IDLE'
    BUFFERING = 'BUFFERING'
    PLAYING = 'PLAYING'
    PAUSED = 'PAUSED'


@dataclass
class ChromecastReceiverState:
    """
    Shared, lock-protected receiver state.
    """

    _lock: threading.RLock = field(default_factory=threading.RLock)

    receiver_state: ReceiverState = ReceiverState.IDLE
    player_state: PlayerState = PlayerState.IDLE
    volume_level: float = 1.0
    muted: bool = False
    media_session_id: int = 0
    current_time: float = 0.0
    duration: Optional[float] = None
    content_id: Optional[str] = None
    content_type: Optional[str] = None
    stream_type: Optional[str] = None
    title: Optional[str] = None
    subtitle_tracks: List[dict] = field(default_factory=list)
    active_track_ids: List[int] = field(default_factory=list)
    application_id: Optional[str] = None
    display_name: Optional[str] = None
    transport_id: Optional[str] = None
    session_id: Optional[str] = None
    status_text: str = RECEIVER_STATUS_IDLE
    _last_update: float = 0.0
    _last_broadcast: Dict[str, Any] = field(default_factory=dict)
    _command_time: float = 0.0

    @property
    def is_active(self) -> bool:
        """
        True when there is an active media session.
        """
        with self._lock:
            return self.receiver_state == ReceiverState.LAUNCHED and bool(
                self.media_session_id
            )

    def update_player_state(self, status: dict) -> bool:
        """
        Update state from a :meth:`MediaPlugin.status()` dictionary.
        Returns ``True`` if the state changed meaningfully.
        """
        with self._lock:
            # Briefly ignore the player status after a command to avoid
            # racing with command-induced state changes.
            if time.time() - self._command_time < 0.5:
                return False

            state = self._get_status_value(status, 'state', 'status', 'playback_state')
            if state:
                state = str(state).lower()
                if state in ('play', 'playing'):
                    self.player_state = PlayerState.PLAYING
                elif state in ('pause', 'paused'):
                    self.player_state = PlayerState.PAUSED
                elif state in ('stop', 'idle'):
                    self.player_state = PlayerState.IDLE
                elif state in ('buffer', 'buffering'):
                    self.player_state = PlayerState.BUFFERING
                else:
                    self.player_state = PlayerState.IDLE

            position = self._get_status_value(
                status, 'position', 'time', 'elapsed', 'current_time'
            )
            if position is not None:
                try:
                    self.current_time = float(position)
                except (TypeError, ValueError):
                    pass

            duration = self._get_status_value(
                status, 'duration', 'length', 'total_time'
            )
            if duration is not None:
                try:
                    self.duration = float(duration)
                except (TypeError, ValueError):
                    self.duration = None

            volume = status.get('volume')
            if volume is not None:
                try:
                    self.volume_level = min(100.0, max(0.0, float(volume))) / 100.0
                except (TypeError, ValueError):
                    pass

            muted = self._get_status_value(status, 'mute', 'muted')
            if muted is not None:
                self.muted = bool(muted)

            self._last_update = time.time()

            # Derive receiver state and status text from the player state.
            # Receiver state is only changed by explicit LAUNCH/STOP protocol
            # messages; player status updates only affect the status text.
            if self.player_state in (PlayerState.PLAYING, PlayerState.PAUSED):
                self.status_text = (
                    RECEIVER_STATUS_PAUSED
                    if self.player_state == PlayerState.PAUSED
                    else RECEIVER_STATUS_PLAYING
                )
            elif self.player_state == PlayerState.BUFFERING:
                self.status_text = 'Buffering'
            else:
                self.receiver_state = ReceiverState.IDLE
                self.status_text = RECEIVER_STATUS_IDLE

            changed = self._state_changed()
            if changed:
                self._last_broadcast = self._snapshot()
            return changed

    def _snapshot(self) -> Dict[str, Any]:
        return {
            'player_state': self.player_state,
            'current_time': round(self.current_time, 2),
            'duration': self.duration,
            'volume_level': self.volume_level,
            'muted': self.muted,
            'media_session_id': self.media_session_id,
            'status_text': self.status_text,
        }

    def _state_changed(self) -> bool:
        return self._last_broadcast != self._snapshot()

    @staticmethod
    def _get_status_value(status: dict, *keys):
        for key in keys:
            if key in status and status[key] is not None:
                return status[key]
        return None

    def set_application(
        self,
        application_id: str,
        display_name: str,
        session_id: str,
        transport_id: str,
    ):
        with self._lock:
            self.application_id = application_id
            self.display_name = display_name
            self.session_id = session_id
            self.transport_id = transport_id
            self.receiver_state = ReceiverState.LAUNCHED
            self._command_time = time.time()

    def clear_application(self):
        with self._lock:
            self.application_id = None
            self.display_name = None
            self.session_id = None
            self.transport_id = None
            self.receiver_state = ReceiverState.IDLE
            self.player_state = PlayerState.IDLE
            self.media_session_id = 0
            self.current_time = 0.0
            self.duration = None
            self.content_id = None
            self.content_type = None
            self.stream_type = None
            self.title = None
            self.subtitle_tracks = []
            self.active_track_ids = []
            self.status_text = RECEIVER_STATUS_IDLE
            self._command_time = time.time()

    def set_media(
        self,
        content_id: str,
        content_type: str,
        title: Optional[str],
        stream_type: str,
        subtitle_tracks: List[dict],
        active_track_ids: List[int],
        current_time: float = 0.0,
    ):
        with self._lock:
            self.media_session_id += 1
            self.content_id = content_id
            self.content_type = content_type
            self.stream_type = stream_type
            self.title = title
            self.subtitle_tracks = subtitle_tracks
            self.active_track_ids = active_track_ids
            self.current_time = float(current_time)
            self.player_state = PlayerState.BUFFERING
            self.status_text = 'Buffering'
            self._command_time = time.time()

    def stop_media(self):
        with self._lock:
            self.player_state = PlayerState.IDLE
            self.media_session_id = 0
            self.current_time = 0.0
            self.content_id = None
            self.content_type = None
            self.stream_type = None
            self.title = None
            self.subtitle_tracks = []
            self.active_track_ids = []
            self.status_text = RECEIVER_STATUS_IDLE
            self._command_time = time.time()

    def get(self) -> Dict[str, Any]:
        with self._lock:
            return self._snapshot()
