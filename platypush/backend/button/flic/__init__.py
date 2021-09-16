from threading import Timer
from time import time

from platypush.backend import Backend
from platypush.message.event.button.flic import FlicButtonEvent

from .fliclib.fliclib import FlicClient, ButtonConnectionChannel, ClickType


class ButtonFlicBackend(Backend):
    """
    Backend that listen for events from the Flic (https://flic.io/) bluetooth
    smart buttons.

    Triggers:

        * :class:`platypush.message.event.button.flic.FlicButtonEvent` when a button is pressed.
            The event will also contain the press sequence
            (e.g. ``["ShortPressEvent", "LongPressEvent", "ShortPressEvent"]``)

    Requires:

        * **fliclib** (https://github.com/50ButtonsEach/fliclib-linux-hci). For the backend to work properly you need to have the ``flicd`` daemon from the fliclib running, and you have to first pair the buttons with your device using any of the scanners provided by the library.

    """

    _long_press_timeout = 0.3
    _btn_timeout = 0.5
    ShortPressEvent = "ShortPressEvent"
    LongPressEvent = "LongPressEvent"

    def __init__(self, server='localhost', long_press_timeout=_long_press_timeout,
                 btn_timeout=_btn_timeout, **kwargs):
        """
        :param server: flicd server host (default: localhost)
        :type server: str

        :param long_press_timeout: How long you should press a button for a press action to be considered "long press" (default: 0.3 secohds)
        :type long_press_timeout: float

        :param btn_timeout: How long since the last button release before considering the user interaction completed (default: 0.5 seconds)
        :type btn_timeout: float
        """

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

        self.logger.info('Initialized Flic buttons backend on {}'.format(self.server))

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
            self.logger.info('Flic event triggered from {}: {}'.format(
                self._btn_addr, self._cur_sequence))

            self.bus.post(FlicButtonEvent(
                btn_addr=self._btn_addr, sequence=self._cur_sequence))

            self._cur_sequence = []

        return _f

    def _on_event(self):
        # noinspection PyUnusedLocal
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

    def run(self):
        super().run()

        self.client.handle_events()


# vim:sw=4:ts=4:et:

