from multiprocessing import Process
from threading import RLock, Timer
from time import time

from platypush.context import get_bus
from platypush.message.event.flic import FlicButtonEvent
from platypush.plugins import RunnablePlugin

from .fliclib import FlicClient, ButtonConnectionChannel, ClickType


class FlicPlugin(RunnablePlugin):
    """
    This integration listens for events from the `Flic <https://flic.io/>`_
    smart buttons over Bluetooth.

    Requires:

        * **fliclib** (https://github.com/50ButtonsEach/fliclib-linux-hci).

    Clone the repository and follow the instructions in the README. This plugin
    requires:

        * The ``flicd`` daemon to be running - either on the same machine or on
          a machine that can be reached through the network.

        * The buttons to be paired with the device running the ``flicd`` daemon.
          The repository provides several scanners, but the easiest way is
          probably through the ``new_scan_wizard.py`` script.

    .. code-block:: bash

      # Clone the repository
      $ git clone https://github.com/50ButtonsEach/fliclib-linux-hci.git
      # Run the flid daemon
      $ [sudo] fliclib-linux-hci/bin/$(uname -m)/flicd -f /path/to/flicd.db &
      # Run the new_scan_wizard.py script to pair the buttons
      $ cd fliclib-linux-hci/clientlib/python
      $ python3 new_scan_wizard.py

    """

    _long_press_timeout = 0.3
    _btn_timeout = 0.5
    ShortPressEvent = "ShortPressEvent"
    LongPressEvent = "LongPressEvent"

    def __init__(
        self,
        server: str = 'localhost',
        long_press_timeout: float = _long_press_timeout,
        btn_timeout: float = _btn_timeout,
        **kwargs,
    ):
        """
        :param server: flicd server host (default: localhost)
        :param long_press_timeout: How long you should press a button for a
            press action to be considered "long press" (default: 0.3 secohds)
        :param btn_timeout: How long since the last button release before
            considering the user interaction completed (default: 0.5 seconds)
        """

        super().__init__(**kwargs)

        self.server = server
        self._client = None
        self._client_lock = RLock()

        self._long_press_timeout = long_press_timeout
        self._btn_timeout = btn_timeout
        self._btn_timer = None
        self._btn_addr = None
        self._down_pressed_time = None
        self._cur_sequence = []

    @property
    def client(self):
        with self._client_lock:
            if not self._client:
                self._client = FlicClient(self.server)
                self._client.get_info(self._received_info)
                self._client.on_new_verified_button = self._got_button

            return self._client

    def _got_button(self, bd_addr):
        cc = ButtonConnectionChannel(bd_addr)
        cc.on_button_up_or_down = (
            lambda channel, click_type, was_queued, time_diff: self._on_event(
                bd_addr, channel, click_type, was_queued, time_diff
            )
        )
        self.client.add_connection_channel(cc)

    def _received_info(self, items):
        for bd_addr in items["bd_addr_of_verified_buttons"]:
            self._got_button(bd_addr)

    def _on_btn_timeout(self):
        if self._btn_addr:
            get_bus().post(
                FlicButtonEvent(
                    btn_addr=self._btn_addr,
                    sequence=self._cur_sequence,
                )
            )

        self._cur_sequence = []

    # _ = channel
    # __ = time_diff
    def _on_event(self, bd_addr, _, click_type, was_queued, __):
        if was_queued and self._btn_addr:
            return

        if self._btn_timer:
            self._btn_timer.cancel()

        if click_type == ClickType.ButtonDown:
            self._down_pressed_time = time()
            return

        btn_event = self.ShortPressEvent
        if self._down_pressed_time:
            if time() - self._down_pressed_time >= self._long_press_timeout:
                btn_event = self.LongPressEvent
            self._down_pressed_time = None

        self._cur_sequence.append(btn_event)
        self._btn_addr = bd_addr
        self._btn_timer = Timer(self._btn_timeout, self._on_btn_timeout)
        self._btn_timer.start()

    def _processor(self):
        try:
            self.client.handle_events()
        except KeyboardInterrupt:
            pass

    def main(self):
        while not self.should_stop():
            proc = Process(target=self._processor, name='FlicProcessor')
            proc.start()
            self.wait_stop()

            if proc.is_alive():
                proc.terminate()
                proc.join(2)

            if proc.is_alive():
                self.logger.warning('Flic processor still alive after termination')
                proc.kill()


# vim:sw=4:ts=4:et:
