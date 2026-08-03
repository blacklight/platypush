import json
import logging
import os
import threading
from typing import Optional

from platypush.plugins.media._chromecast_receiver._config import get_dial_state_path

from ._apps import DialAppRegistry
from ._ssdp import SsdpResponder

logger = logging.getLogger(__name__)


class DialService:
    """
    Lifecycle coordinator for the DIAL layer.
    Owns: SsdpResponder, DialAppRegistry, state file.
    """

    def __init__(self, config):
        """
        Parameters
        ----------
        config:
            ChromecastReceiverConfig (with populated .dial).
        """
        self._config = config
        self.registry = DialAppRegistry(config.dial.supported_apps)
        self._ssdp = SsdpResponder(config)
        self._state_path = get_dial_state_path()
        self._lock = threading.Lock()
        self._state_dir_ensured = False

    def start(self):
        logger.info(
            'Starting DIAL service (apps: %s)',
            ', '.join(self.registry.list_app_ids()),
        )
        self._ssdp.start()
        self.flush_state()

    def stop(self):
        logger.info('Stopping DIAL service')
        self._ssdp.stop()
        try:
            self._write_state(None, None)
        except Exception as e:
            logger.debug('Could not clear DIAL state on stop: %s', e)

    def flush_state(self):
        """Write current registry state to the state file."""
        active = self.registry.get_active_app()
        if active:
            self._write_state(active.name, active.run_id)
        else:
            self._write_state(None, None)

    def _ensure_state_dir(self):
        if not self._state_dir_ensured:
            os.makedirs(os.path.dirname(self._state_path), exist_ok=True)
            self._state_dir_ensured = True

    def _write_state(self, active_app: Optional[str], run_id: Optional[str]):
        self._ensure_state_dir()
        tmp = self._state_path + '.tmp'
        data = json.dumps({'active_app': active_app, 'run_id': run_id})
        try:
            with open(tmp, 'w') as f:
                f.write(data)
            os.replace(tmp, self._state_path)
        except OSError as e:
            logger.warning('Could not write DIAL state file: %s', e)
