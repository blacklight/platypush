import logging
import threading
from typing import Any, Callable, Dict, List, Optional

from platypush.context import get_backend, get_bus
from platypush.message import Message
from platypush.plugins import Plugin
from platypush.utils import get_redis

from ._advertiser import ChromecastReceiverAdvertiser
from ._config import ChromecastReceiverConfig
from ._dial._messages import (
    DialLaunchReply,
    DialLaunchRequest,
    DialStopReply,
    DialStopRequest,
)
from ._dial._service import DialService
from ._server import ChromecastReceiverServer
from ._session import CastSession
from ._state import ChromecastReceiverState, PlayerState

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

        self._dial_service: Optional[DialService] = None
        self._dial_bus_unregisters: List[Callable[[], None]] = []

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

        if self.config.dial.enabled:
            self._dial_service = DialService(self.config)
            self._dial_service.start()
            self._register_bus_handlers()

        self._status_thread = threading.Thread(
            target=self._status_loop, name='ChromecastStatusLoop', daemon=True
        )
        self._status_thread.start()

    def stop(self):
        if not self.config.enabled:
            return

        logger.info('Stopping Chromecast receiver')
        self.should_stop.set()

        if self._dial_service:
            self._dial_service.stop()
            self._dial_service = None

        for unregister in self._dial_bus_unregisters:
            try:
                unregister()
            except Exception as e:
                logger.debug('Error unregistering DIAL bus handler: %s', e)
        self._dial_bus_unregisters.clear()

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
            self._status_loop_iteration()
            self.should_stop.wait(self.config.status_interval)

    def _status_loop_iteration(self):
        try:
            status = self._get_plugin_status()
            if status:
                changed = self.state.update_player_state(status)
                self._update_advertisement()

                is_idle = self.state.player_state == PlayerState.IDLE
                if self._dial_service:
                    if is_idle:
                        # Only clear DIAL state if we are past the launch
                        # grace period.  This prevents an idle poll that
                        # arrives before the media backend has transitioned
                        # to playing from prematurely marking the app as
                        # stopped.
                        if not self._dial_service.registry.within_launch_grace():
                            self._dial_service.registry.notify_playback_stopped()
                            self._dial_service.flush_state()
                    else:
                        # Playback is active — record the observation so
                        # the grace window is no longer needed.
                        self._dial_service.registry.notify_playback_active()

                if changed:
                    logger.info(
                        'Broadcasting media status: state=%s',
                        self.state.player_state,
                    )
                    self.broadcast_media_status()
        except Exception as e:
            logger.debug('Error polling media status: %s', e)

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

    # ------------------------------------------------------------------
    # DIAL bus handlers
    # ------------------------------------------------------------------

    def _register_bus_handlers(self):
        self._dial_bus_unregisters = [
            get_bus().register_handler(DialLaunchRequest, self._handle_dial_launch),
            get_bus().register_handler(DialStopRequest, self._handle_dial_stop),
        ]

    def _handle_dial_launch(self, msg: DialLaunchRequest):
        if not self._dial_service:
            reply = DialLaunchReply(
                success=False,
                error='DIAL service is not running',
                reply_topic=msg.reply_topic,
            )
            self._send_reply(msg.reply_topic, reply)
            return

        try:
            run_id = self._dial_service.registry.launch(
                msg.app_id, msg.raw_payload, self.plugin
            )
            self._dial_service.flush_state()
            reply = DialLaunchReply(
                success=True,
                run_id=run_id,
                reply_topic=msg.reply_topic,
            )
        except (KeyError, ValueError, RuntimeError) as e:
            reply = DialLaunchReply(
                success=False,
                error=str(e),
                client_error=isinstance(e, (KeyError, ValueError)),
                reply_topic=msg.reply_topic,
            )

        self._send_reply(msg.reply_topic, reply)

    def _handle_dial_stop(self, msg: DialStopRequest):
        if not self._dial_service:
            reply = DialStopReply(
                success=False,
                error='DIAL service is not running',
                reply_topic=msg.reply_topic,
            )
            self._send_reply(msg.reply_topic, reply)
            return

        try:
            self._dial_service.registry.stop(msg.app_id, self.plugin)
            self._dial_service.flush_state()
            reply = DialStopReply(
                success=True,
                reply_topic=msg.reply_topic,
            )
        except (KeyError, ValueError, RuntimeError) as e:
            reply = DialStopReply(
                success=False,
                error=str(e),
                client_error=isinstance(e, (KeyError, ValueError)),
                reply_topic=msg.reply_topic,
            )

        self._send_reply(msg.reply_topic, reply)

    @staticmethod
    def _send_reply(queue_name: str, reply: Message):
        try:
            redis = get_redis()
            redis.rpush(queue_name, str(reply))
        except Exception as e:
            logger.warning('Could not send DIAL reply to %s: %s', queue_name, e)
