"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
"""

import cwiid
import re
import time

from platypush.backend import Backend
from platypush.message import Message
from platypush.message.event.wiimote import WiimoteEvent
from platypush.message.request import Request


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


    def msg_callback(self):
        def _callback(msg_list, timestamp):
            print(msg_list)

        return _callback

    def get_wiimote(self):
        if not self._wiimote:
            self._wiimote = cwiid.Wiimote()
            self._wiimote.mesg_callback = self.msg_callback()
            # self._wiimote.enable(cwiid.FLAG_MESG_IFC | cwiid.FLAG_MOTIONPLUS)
            self._wiimote.enable(cwiid.FLAG_MOTIONPLUS)
            self._wiimote.rpt_mode = cwiid.RPT_ACC | cwiid.RPT_BTN | cwiid.RPT_MOTIONPLUS

            self.logger.info('WiiMote connected')
            self._wiimote.led = 1
            self._wiimote.rumble = True
            time.sleep(0.5)
            self._wiimote.rumble = False

        return self._wiimote

    def get_state(self):
        wm = self.get_wiimote()
        state = wm.state
        parsed_state = {}

        # Get buttons
        all_btns = [attr for attr in dir(cwiid) if attr.startswith('BTN_')]
        parsed_state['buttons'] = { btn: True for btn in all_btns
                if state.get('buttons', 0) & getattr(cwiid, btn) != 0 }

        # Get LEDs
        all_leds = [attr for attr in dir(cwiid) if re.match('LED\d_ON', attr)]
        parsed_state['led'] = { led[:4]: True for led in all_leds
                if state.get('leds', 0) & getattr(cwiid, led) != 0 }

        # Get errors
        all_errs = [attr for attr in dir(cwiid) if attr.startswith('ERROR_')]
        parsed_state['error'] = { err: True for err in all_errs
                if state.get('errs', 0) & getattr(cwiid, err) != 0 }

        parsed_state['battery'] = round(state.get('battery', 0)/cwiid.BATTERY_MAX, 3)
        parsed_state['rumble'] = bool(state.get('rumble', 0))

        if 'acc' in state:
            parsed_state['acc'] = tuple(int(acc/5)*5 for acc in state['acc'])

        if 'motionplus' in state:
            parsed_state['motionplus'] = {
                'angle_rate': tuple(int(angle/100) for angle
                                    in state['motionplus']['angle_rate']),
                'low_speed': state['motionplus']['low_speed'],
            }

        return parsed_state


    def run(self):
        super().run()
        connection_attempts = 0
        last_state = {}

        while not self.should_stop():
            try:
                state = self.get_state()
                changed_state = { k: state[k] for k in state.keys()
                                 if state[k] != last_state.get(k) }

                if changed_state:
                    self.bus.post(WiimoteEvent(**changed_state))
                connection_attempts = 0
                last_state = state
                time.sleep(0.1)
            except RuntimeError as e:
                if type(e) == RuntimeError and str(e) == 'Error opening wiimote connection':
                    if connection_attempts == 0:
                        self.logger.info('Press 1+2 to pair your WiiMote controller')
                else:
                    self.logger.exception(e)
                self._wiimote = None
                connection_attempts += 1

# vim:sw=4:ts=4:et:

