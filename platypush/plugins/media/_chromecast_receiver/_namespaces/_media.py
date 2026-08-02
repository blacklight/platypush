import logging
import time

from platypush.message.event.media import (
    MediaPauseEvent,
    MediaPlayEvent,
    MediaResumeEvent,
    MediaStopEvent,
)
from platypush.plugins.media._chromecast_receiver._constants import NAMESPACE_MEDIA
from platypush.plugins.media._chromecast_receiver._media import resolve_media
from platypush.plugins.media._chromecast_receiver._state import PlayerState
from platypush.plugins.media._chromecast_receiver._status import build_media_status

from ._base import NamespaceHandler

logger = logging.getLogger(__name__)


class MediaNamespace(NamespaceHandler):
    namespace = NAMESPACE_MEDIA

    def _handle_GET_STATUS(self, session, message, source_id, destination_id):
        self.send(
            session,
            build_media_status(
                self.state,
                self.request_id(message),
            ),
            destination_id,
            source_id,
            namespace=NAMESPACE_MEDIA,
        )

    def _handle_LOAD(self, session, message, source_id, destination_id):
        media = message.get('media', {})
        logger.info(
            'LOAD message from %s: contentId=%r contentType=%r streamType=%r tracks=%r metadata=%r',
            source_id,
            media.get('contentId'),
            media.get('contentType'),
            media.get('streamType'),
            media.get('tracks'),
            media.get('metadata'),
        )
        content_id = media.get('contentId')
        if not content_id:
            self._send_error(session, message, 'LOAD_FAILED', 'Missing contentId')
            return

        content_type = media.get('contentType')
        stream_type = media.get('streamType', 'BUFFERED')
        current_time = float(message.get('currentTime', 0) or 0)
        autoplay = bool(message.get('autoplay', True))
        active_track_ids = message.get('activeTrackIds', [])
        metadata = media.get('metadata') or {}
        tracks = media.get('tracks', [])

        try:
            resolved = resolve_media(
                self.plugin,
                self.config.media_base_url,
                content_id,
                content_type,
                stream_type,
                current_time,
                autoplay,
                tracks,
                metadata,
            )
        except Exception as e:
            logger.exception('Failed to resolve media: %s', e)
            self._send_error(session, message, 'LOAD_FAILED', str(e))
            return

        # Ensure active track IDs match the resolved subtitle tracks
        if resolved['active_track_ids']:
            active_track_ids = resolved['active_track_ids']
        elif active_track_ids and not resolved['active_track_ids']:
            resolved['active_track_ids'] = active_track_ids

        try:
            kwargs = {
                'subtitles': resolved.get('subtitle_url'),
                'title': resolved.get('title'),
            }

            logger.info(
                'Playing resolved URL %r (content_type=%r, stream_type=%r)',
                resolved['resolved_url'],
                resolved.get('content_type'),
                resolved.get('stream_type'),
            )
            self.plugin.play(resolved['resolved_url'], **kwargs)

            if resolved.get('current_time', 0) > 0:
                self._seek(resolved['current_time'])

            if not resolved.get('autoplay', True):
                self.plugin.pause()
        except Exception as e:
            logger.exception('Failed to load media on plugin: %s', e)
            self._send_error(session, message, 'LOAD_FAILED', str(e))
            return

        self.state.set_media(
            content_id=resolved['resolved_url'],
            content_type=resolved['content_type'],
            title=resolved['title'],
            stream_type=resolved['stream_type'],
            subtitle_tracks=resolved['subtitle_tracks'],
            active_track_ids=resolved['active_track_ids'],
            current_time=resolved.get('current_time', 0.0),
        )

        if resolved.get('autoplay', True):
            self.plugin.post_event(
                MediaPlayEvent,
                resource=resolved['resolved_url'],
                title=resolved['title'],
            )
        else:
            with self.state._lock:
                self.state.player_state = PlayerState.PAUSED
                self.state.status_text = 'Paused'
                self.state._command_time = time.time()

            self.plugin.post_event(
                MediaPauseEvent,
                resource=resolved['resolved_url'],
                title=resolved['title'],
            )

        session.active_namespaces.add(NAMESPACE_MEDIA)

        self.send(
            session,
            build_media_status(
                self.state,
                self.request_id(message),
            ),
            destination_id,
            source_id,
            namespace=NAMESPACE_MEDIA,
        )

    def _handle_PLAY(self, session, message, source_id, destination_id):
        try:
            self.plugin.play()
        except Exception as e:
            logger.warning('Error resuming playback: %s', e)

        with self.state._lock:
            self.state.player_state = PlayerState.PLAYING
            self.state.status_text = 'Playing'
            self.state._command_time = time.time()

        self.plugin.post_event(
            MediaResumeEvent,
            resource=self.state.content_id,
            title=self.state.title,
        )

        self._reply_status(session, message, source_id, destination_id)

    def _handle_PAUSE(self, session, message, source_id, destination_id):
        try:
            self.plugin.pause()
        except Exception as e:
            logger.warning('Error pausing playback: %s', e)

        with self.state._lock:
            self.state.player_state = PlayerState.PAUSED
            self.state.status_text = 'Paused'
            self.state._command_time = time.time()

        self.plugin.post_event(
            MediaPauseEvent,
            resource=self.state.content_id,
            title=self.state.title,
        )

        self._reply_status(session, message, source_id, destination_id)

    def _handle_STOP(self, session, message, source_id, destination_id):
        try:
            self.plugin.stop()
        except Exception as e:
            logger.warning('Error stopping playback: %s', e)

        self.state.stop_media()
        session.active_namespaces.discard(NAMESPACE_MEDIA)

        self.plugin.post_event(
            MediaStopEvent,
            resource=self.state.content_id,
            title=self.state.title,
        )

        self._reply_status(session, message, source_id, destination_id)

    def _handle_SEEK(self, session, message, source_id, destination_id):
        current_time = float(message.get('currentTime', 0) or 0)
        if not self._seek(current_time):
            self._send_error(session, message, 'INVALID_REQUEST', 'Seek failed')
            return

        with self.state._lock:
            self.state.current_time = current_time
            self.state._command_time = time.time()

        self._reply_status(session, message, source_id, destination_id)

    def _handle_SET_VOLUME(self, session, message, source_id, destination_id):
        volume = message.get('volume', {})
        level = volume.get('level')

        try:
            if level is not None:
                with self.state._lock:
                    self.state.volume_level = min(1.0, max(0.0, float(level)))
                    self.state._command_time = time.time()
                self.plugin.set_volume(volume=int(self.state.volume_level * 100))
        except Exception as e:
            logger.warning('Error setting media volume: %s', e)

        self._reply_status(session, message, source_id, destination_id)

    def _seek(self, position: float) -> bool:
        for method in ('set_position', 'seek'):
            try:
                getattr(self.plugin, method)(position)
                return True
            except Exception as e:
                logger.debug('Seek method %s failed: %s', method, e)

        return False

    def _reply_status(self, session, message, source_id, destination_id):
        self.send(
            session,
            build_media_status(
                self.state,
                self.request_id(message),
            ),
            destination_id,
            source_id,
            namespace=NAMESPACE_MEDIA,
        )

    def _send_error(self, session, message, error_type, reason):
        self.send(
            session,
            {
                'type': error_type,
                'requestId': self.request_id(message),
                'customData': {'reason': reason},
            },
            session.transport_id or 'receiver-0',
            session.sender_id or 'sender-0',
            namespace=NAMESPACE_MEDIA,
        )
