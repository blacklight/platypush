import time

from platypush.context import get_backend
from platypush.plugins import Plugin, action


class WiimotePlugin(Plugin):
    """
    WiiMote plugin.
    A wrapper around the :mod:`platypush.backend.wiimote` backend to
    programmatically control a Nintendo WiiMote.

    It requires the WiiMote backend to be enabled.
    """

    @classmethod
    def _get_wiimote(cls):
        return get_backend('wiimote').get_wiimote()

    @action
    def connect(self):
        """
        Connects to the WiiMote
        """
        self._get_wiimote()

    @action
    def close(self):
        """
        Closes the connection with the WiiMote
        """
        get_backend('wiimote').close()

    @action
    def rumble(self, secs):
        """
        Rumbles the controller for the specified number of seconds
        """
        wm = self._get_wiimote()
        wm.rumble = True
        time.sleep(secs)
        wm.rumble = False

    @action
    def state(self):
        """
        Return the state of the controller
        """
        return get_backend('wiimote').get_state()

    @action
    def set_leds(self, leds):
        """
        Set the LEDs state on the controller

        :param leds: Iterable with the new states to be applied to the LEDs.
            Example: [1, 0, 0, 0] or (False, True, False, False)
        :type leds: list
        """

        new_led = 0
        for i, led in enumerate(leds):
            if led:
                new_led |= 1 << i

        self._get_wiimote().led = new_led


# vim:sw=4:ts=4:et:
