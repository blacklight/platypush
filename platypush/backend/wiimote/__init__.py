import re
import time

from platypush.backend import Backend
from platypush.message.event.wiimote import (
    WiimoteEvent,
    WiimoteConnectionEvent,
    WiimoteDisconnectionEvent,
)


class WiimoteBackend(Backend):
    """
    Backend to communicate with a Nintendo WiiMote controller

    Triggers:

        * :class:`platypush.message.event.Wiimote.WiimoteEvent` \
            when the state of the Wiimote (battery, buttons, acceleration etc.) changes

    Requires:

        * **python3-wiimote** (follow instructions at https://github.com/azzra/python3-wiimote)
    """

    _wiimote = None
    _inactivity_timeout = 300
    _connection_attempts = 0
    _last_btn_event_time = 0
    _bdaddr = None

    def __init__(
        self, bdaddr=_bdaddr, inactivity_timeout=_inactivity_timeout, *args, **kwargs
    ):
        """
        :param bdaddr: If set, connect to this specific Wiimote physical address (example: 00:11:22:33:44:55)
        :type bdaddr: str

        :param inactivity_timeout: Number of seconds elapsed from the last Wiimote action before disconnecting the
            device (default: 300 seconds)
        :type inactivity_timeout: float
        """

        super().__init__(*args, **kwargs)
        self._bdaddr = bdaddr
        self._inactivity_timeout = inactivity_timeout

    def get_wiimote(self):
        import cwiid

        if not self._wiimote:
            if self._bdaddr:
                self._wiimote = cwiid.Wiimote(bdaddr=self._bdaddr)
            else:
                self._wiimote = cwiid.Wiimote()

            self._wiimote.enable(cwiid.FLAG_MOTIONPLUS)
            self._wiimote.rpt_mode = (
                cwiid.RPT_ACC | cwiid.RPT_BTN | cwiid.RPT_MOTIONPLUS
            )

            self.logger.info('WiiMote connected')
            self._last_btn_event_time = time.time()
            self.bus.post(WiimoteConnectionEvent())

        return self._wiimote

    def get_state(self):
        import cwiid

        wm = self.get_wiimote()
        state = wm.state
        parsed_state = {}

        # Get buttons
        all_btns = [attr for attr in dir(cwiid) if attr.startswith('BTN_')]
        parsed_state['buttons'] = {
            btn: True
            for btn in all_btns
            if state.get('buttons', 0) & getattr(cwiid, btn) != 0
        }

        # Get LEDs
        all_leds = [attr for attr in dir(cwiid) if re.match(r'LED\d_ON', attr)]
        parsed_state['led'] = {
            led[:4]: True
            for led in all_leds
            if state.get('leds', 0) & getattr(cwiid, led) != 0
        }

        # Get errors
        all_errs = [attr for attr in dir(cwiid) if attr.startswith('ERROR_')]
        parsed_state['error'] = {
            err: True
            for err in all_errs
            if state.get('errs', 0) & getattr(cwiid, err) != 0
        }

        parsed_state['battery'] = round(state.get('battery', 0) / cwiid.BATTERY_MAX, 3)
        parsed_state['rumble'] = bool(state.get('rumble', 0))

        if 'acc' in state:
            parsed_state['acc'] = tuple(int(acc / 5) * 5 for acc in state['acc'])

        if 'motionplus' in state:
            parsed_state['motionplus'] = {
                'angle_rate': tuple(
                    int(angle / 100) for angle in state['motionplus']['angle_rate']
                ),
                'low_speed': state['motionplus']['low_speed'],
            }

        return parsed_state

    def close(self):
        if not self._wiimote:
            return

        try:
            self._wiimote.close()
        except Exception as e:
            self.logger.warning('Could not close Wiimote connection: {}'.format(str(e)))

        self._wiimote = None
        self.bus.post(WiimoteDisconnectionEvent())

    def run(self):
        super().run()

        self._connection_attempts = 0
        last_state = {}
        self.logger.info('Initialized Wiimote backend')

        while not self.should_stop():
            try:
                state = self.get_state()
                changed_state = {
                    k: state[k] for k in state.keys() if state[k] != last_state.get(k)
                }

                if changed_state:
                    self.bus.post(WiimoteEvent(**changed_state))

                if 'buttons' in changed_state:
                    self._last_btn_event_time = time.time()
                elif (
                    last_state
                    and time.time() - self._last_btn_event_time
                    >= self._inactivity_timeout
                ):
                    self.logger.info('Wiimote disconnected upon timeout')
                    self.close()

                last_state = state
                time.sleep(0.1)
            except RuntimeError as e:
                if (
                    type(e) == RuntimeError
                    and str(e) == 'Error opening wiimote connection'
                ):
                    if self._connection_attempts == 0:
                        self.logger.info('Press 1+2 to pair your WiiMote controller')
                else:
                    self.logger.exception(e)

                self.close()
                self._connection_attempts += 1


# vim:sw=4:ts=4:et:
