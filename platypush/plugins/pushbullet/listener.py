import logging
import time
from typing import Callable, Optional

from pushbullet import Listener as _Listener


class Listener(_Listener):
    """
    Extends the Pushbullet Listener object by adding ``on_open`` and ``on_close`` handlers.
    """

    def __init__(
        self,
        *args,
        on_open: Optional[Callable[[], None]] = None,
        on_close: Optional[Callable[[], None]] = None,
        **kwargs,
    ):
        kwargs['on_error'] = self._err_callback()
        super().__init__(*args, **kwargs)
        self._on_open_hndl = on_open
        self._on_close_hndl = on_close
        self.logger = logging.getLogger(__name__)

    def _on_open(self):
        def callback(*_):
            self.connected = True
            self.last_update = time.time()
            if self._on_open_hndl:
                self._on_open_hndl()

        return callback

    def _on_close(self):
        def callback(*_):
            self.connected = False
            if self._on_close_hndl:
                try:
                    self._on_close_hndl()
                except Exception as e:
                    self.logger.warning('Pushbullet listener close error: %s', e)

        return callback

    def _err_callback(self):
        def callback(e):
            self.logger.error('Pushbullet listener error: %s: %s', type(e).__name__, e)

        return callback


# vim:sw=4:ts=4:et:
