import importlib
import logging

from enum import Enum
from threading import Timer
from time import time

from platypush.backend import Backend
from platypush.message.event.button.flic import FlicButtonEvent

from .fliclib.fliclib import FlicClient, ButtonConnectionChannel, ClickType


class ButtonFlicBackend(Backend):
    _long_press_timeout = 0.3
    _btn_timeout = 0.5
    ShortPressEvent = "ShortPressEvent"
    LongPressEvent = "LongPressEvent"

    def __init__(self, server, long_press_timeout=_long_press_timeout,
                 btn_timeout=_btn_timeout, **kwargs):
        super().__init__(**kwargs)

        self.server = server
        self.client = FlicClient(server)
        self.client.get_info(self._received_info())
        self.client.on_new_verified_button = self._got_button()

        self._long_press_timeout = long_press_timeout
        self._btn_timeout = btn_timeout
        self._btn_timer = None
        self._btn_addr = None
        self._down_pressed_time = None
        self._cur_sequence = []

        logging.info('Initialized Flic buttons backend on {}'.format(self.server))

    def _got_button(self):
        def _f(bd_addr):
            cc = ButtonConnectionChannel(bd_addr)
            cc.on_button_up_or_down = \
                lambda channel, click_type, was_queued, time_diff: \
                self._on_event()(bd_addr, channel, click_type, was_queued, time_diff)
            self.client.add_connection_channel(cc)

        return _f

    def _received_info(self):
        def _f(items):
            for bd_addr in items["bd_addr_of_verified_buttons"]:
                self._got_button()(bd_addr)
        return _f

    def _on_btn_timeout(self):
        def _f():
            logging.info('Flic event triggered from {}: {}'.format(
                self._btn_addr, self._cur_sequence))

            self.bus.post(FlicButtonEvent(
                btn_addr=self._btn_addr, sequence=self._cur_sequence))

            self._cur_sequence = []

        return _f

    def _on_event(self):
        def _f(bd_addr, channel, click_type, was_queued, time_diff):
            if was_queued:
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
            self._btn_timer = Timer(self._btn_timeout, self._on_btn_timeout())
            self._btn_timer.start()

        return _f

    def send_message(self, msg):
        pass

    def run(self):
        super().run()

        self.client.handle_events()


# vim:sw=4:ts=4:et:

