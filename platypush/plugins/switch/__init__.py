from .. import Plugin

class SwitchPlugin(Plugin):
    """
    Abstract class for interacting with switch devices
    """

    def on(self, args):
        """ Turn the device on """
        raise NotImplementedError()

    def off(self, args):
        """ Turn the device off """
        raise NotImplementedError()

    def toggle(self, args):
        """ Toggle the device status (on/off) """
        raise NotImplementedError()

    def status(self):
        """ Get the device state """
        raise NotImplementedError()


# vim:sw=4:ts=4:et:

