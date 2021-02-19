from abc import ABC

from platypush.plugins import action
from platypush.plugins.switch import SwitchPlugin


class LightPlugin(SwitchPlugin, ABC):
    """
    Abstract plugin to interface your logic with lights/bulbs.
    """

    @action
    def on(self):
        """ Turn the light on """
        raise NotImplementedError()

    @action
    def off(self):
        """ Turn the light off """
        raise NotImplementedError()

    @action
    def toggle(self):
        """ Toggle the light status (on/off) """
        raise NotImplementedError()


# vim:sw=4:ts=4:et:
