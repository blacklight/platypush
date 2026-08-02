import logging
import time

from platypush.plugins.media._chromecast_receiver._constants import (
    DEFAULT_APP_ID,
    DEFAULT_DISPLAY_NAME,
    NAMESPACE_RECEIVER,
)
from platypush.plugins.media._chromecast_receiver._status import build_receiver_status

from ._base import NamespaceHandler

logger = logging.getLogger(__name__)


class ReceiverNamespace(NamespaceHandler):
    namespace = NAMESPACE_RECEIVER

    def _handle_GET_STATUS(self, session, message, source_id, destination_id):
        self.send(
            session,
            build_receiver_status(
                self.state,
                self.request_id(message),
            ),
            destination_id,
            source_id,
        )

    def _handle_LAUNCH(self, session, message, source_id, destination_id):
        app_id = message.get('appId')
        if app_id != DEFAULT_APP_ID:
            self.send(
                session,
                {
                    'type': 'LAUNCH_ERROR',
                    'requestId': self.request_id(message),
                    'reason': 'APP_ERROR',
                    'appId': app_id,
                    'description': f'Unsupported app ID: {app_id}',
                },
                destination_id,
                source_id,
            )
            return

        session.launch_app(DEFAULT_APP_ID, DEFAULT_DISPLAY_NAME)
        self.send(
            session,
            build_receiver_status(
                self.state,
                self.request_id(message),
            ),
            destination_id,
            source_id,
        )

    def _handle_STOP(self, session, message, source_id, destination_id):
        if self.state.is_active:
            try:
                self.plugin.stop()
            except Exception as e:
                logger.warning('Error stopping media on receiver STOP: %s', e)

        session.stop_app()
        self.send(
            session,
            build_receiver_status(
                self.state,
                self.request_id(message),
            ),
            destination_id,
            source_id,
        )

    def _handle_GET_APP_AVAILABILITY(self, session, message, source_id, destination_id):
        """
        Handle GET_APP_AVAILABILITY requests from Cast SDK senders.

        Cast SDK v3 senders (Netflix, Tidal, Jellyfin, etc.) send this message
        immediately after connecting to determine which apps the receiver
        supports. If no response is sent, the sender hides the device from
        the cast picker.

        We respond APP_AVAILABLE for the Default Media Receiver (CC1AD845)
        and APP_UNAVAILABLE for everything else.
        """
        app_ids = message.get('appId', [])
        if isinstance(app_ids, str):
            app_ids = [app_ids]

        availability = {}
        for app_id in app_ids:
            if app_id == DEFAULT_APP_ID:
                availability[app_id] = 'APP_AVAILABLE'
            else:
                availability[app_id] = 'APP_UNAVAILABLE'

        self.send(
            session,
            {
                'type': 'RECEIVER_STATUS',
                'requestId': self.request_id(message),
                'availability': availability,
            },
            destination_id,
            source_id,
        )

    def _handle_SET_VOLUME(self, session, message, source_id, destination_id):
        volume = message.get('volume', {})
        level = volume.get('level')
        muted = volume.get('muted')

        try:
            with self.state._lock:
                prev_muted = self.state.muted
                if muted is not None:
                    self.state.muted = bool(muted)
                if level is not None:
                    self.state.volume_level = min(1.0, max(0.0, float(level)))
                self.state._command_time = time.time()

            if muted is not None and bool(muted) != prev_muted:
                self.plugin.mute()

            if level is not None and not self.state.muted:
                self.plugin.set_volume(volume=int(self.state.volume_level * 100))
        except Exception as e:
            logger.warning('Error setting receiver volume: %s', e)

        self.send(
            session,
            build_receiver_status(
                self.state,
                self.request_id(message),
            ),
            destination_id,
            source_id,
        )
