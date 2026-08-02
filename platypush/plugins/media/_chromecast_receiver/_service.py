import logging
import threading
from typing import Any, Dict, List, Optional

from platypush.context import get_backend
from platypush.plugins import Plugin

from ._advertiser import ChromecastReceiverAdvertiser
from ._config import ChromecastReceiverConfig
from ._server import ChromecastReceiverServer
from ._session import CastSession
from ._state import ChromecastReceiverState

logger = logging.getLogger(__name__)


class ChromecastReceiverService:
    """
    Lifecycle coordinator for the Chromecast receiver.
    """

    def __init__(self, plugin: Plugin, config: Optional[Dict[str, Any]] = None):
        self.plugin = plugin
        self.config = ChromecastReceiverConfig.build(plugin, config)
        self.state = ChromecastReceiverState()
        self.should_stop = threading.Event()

        self._advertiser = ChromecastReceiverAdvertiser(self.config)
        self._server = ChromecastReceiverServer(self)
        self._status_thread: Optional[threading.Thread] = None
        self.sessions: List[CastSession] = []
        self._lock = threading.RLock()
        self._was_active = False

    def start(self):
        if not self.config.enabled:
            return

        if not get_backend('http'):
            raise AssertionError(
                'Chromecast receiver requires the HTTP backend to be configured'
            )

        logger.info('Starting Chromecast receiver for %s', self.config.device_name)

        self._server.start()
        self._advertiser.start(self.state)
        self._status_thread = threading.Thread(
            target=self._status_loop, name='ChromecastStatusLoop', daemon=True
        )
        self._status_thread.start()

    def stop(self):
        if not self.config.enabled:
            return

        logger.info('Stopping Chromecast receiver')
        self.should_stop.set()

        self._server.stop()
        self._advertiser.stop()

        with self._lock:
            sessions = list(self.sessions)
            self.sessions.clear()

        for session in sessions:
            try:
                session.close()
            except Exception as e:
                logger.debug('Error closing session: %s', e)

        if self._status_thread and self._status_thread.is_alive():
            self._status_thread.join(timeout=2.0)

    def _status_loop(self):
        while not self.should_stop.is_set():
            try:
                status = self._get_plugin_status()
                if status:
                    changed = self.state.update_player_state(status)
                    self._update_advertisement()

                    if changed:
                        logger.info(
                            'Broadcasting media status: state=%s',
                            self.state.player_state,
                        )
                        self.broadcast_media_status()
            except Exception as e:
                logger.debug('Error polling media status: %s', e)

            self.should_stop.wait(self.config.status_interval)

    def _get_plugin_status(self) -> Optional[Dict[str, Any]]:
        try:
            result = self.plugin.status()
        except Exception as e:
            logger.debug('Could not get plugin status: %s', e)
            return None

        if result is None:
            return None

        # Some actions wrap their output in a Response object
        if hasattr(result, 'output'):
            result = result.output

        if isinstance(result, dict):
            return result

        return None

    def _update_advertisement(self):
        is_active = self.state.is_active
        if is_active != self._was_active:
            self._was_active = is_active
            self._advertiser.update(self.state)

    def broadcast_media_status(self):
        with self._lock:
            sessions = list(self.sessions)

        for session in sessions:
            try:
                session.send_media_status()
            except Exception as e:
                logger.debug('Error sending media status: %s', e)

    def on_session_closed(self, session: CastSession):
        with self._lock:
            if session in self.sessions:
                self.sessions.remove(session)
