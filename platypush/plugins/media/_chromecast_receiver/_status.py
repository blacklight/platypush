import logging
from typing import Any, Dict, Optional

from ._constants import (
    DEFAULT_APP_ID,
    DEFAULT_DISPLAY_NAME,
    NAMESPACE_MEDIA,
    STREAM_TYPE_BUFFERED,
    SUPPORTED_MEDIA_COMMANDS,
)
from ._state import ChromecastReceiverState, PlayerState

logger = logging.getLogger(__name__)


def _player_state_name(state: PlayerState) -> str:
    return state.value


def build_receiver_status(
    state: ChromecastReceiverState,
    request_id: int = 0,
) -> Dict[str, Any]:
    """
    Build a ``RECEIVER_STATUS`` payload.
    """
    with state._lock:
        applications = []
        if state.receiver_state.name == 'LAUNCHED' and state.transport_id:
            applications.append(
                {
                    'appId': state.application_id or DEFAULT_APP_ID,
                    'displayName': state.display_name or DEFAULT_DISPLAY_NAME,
                    'isIdleScreen': False,
                    'namespaces': [{'name': NAMESPACE_MEDIA}],
                    'sessionId': state.session_id or state.transport_id,
                    'statusText': state.status_text,
                    'transportId': state.transport_id,
                }
            )

        return {
            'type': 'RECEIVER_STATUS',
            'requestId': request_id,
            'status': {
                'applications': applications,
                'volume': {
                    'level': state.volume_level,
                    'muted': state.muted,
                },
            },
        }


def _build_media_item(
    state: ChromecastReceiverState,
) -> Optional[Dict[str, Any]]:
    with state._lock:
        if not state.media_session_id:
            return None

        metadata = {}
        if state.title:
            metadata['metadataType'] = 0
            metadata['title'] = state.title

        media = {
            'contentId': state.content_id or '',
            'contentType': state.content_type or 'video/mp4',
            'streamType': state.stream_type or STREAM_TYPE_BUFFERED,
            'metadata': metadata,
        }

        if state.subtitle_tracks:
            media['tracks'] = state.subtitle_tracks

        return {
            'mediaSessionId': state.media_session_id,
            'playbackRate': 1,
            'playerState': _player_state_name(state.player_state),
            'currentTime': state.current_time,
            'supportedMediaCommands': SUPPORTED_MEDIA_COMMANDS,
            'volume': {
                'level': state.volume_level,
                'muted': state.muted,
            },
            'media': media,
            'activeTrackIds': state.active_track_ids,
        }


def build_media_status(
    state: ChromecastReceiverState,
    request_id: int = 0,
) -> Dict[str, Any]:
    """
    Build a ``MEDIA_STATUS`` payload.
    """
    item = _build_media_item(state)
    return {
        'type': 'MEDIA_STATUS',
        'requestId': request_id,
        'status': [item] if item else [],
    }
