from platypush.plugins import Plugin, action

class SwitchPlugin(Plugin):
    """
    Abstract class for interacting with switch devices
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @action
    def on(self, args):
        """ Turn the device on """
        raise NotImplementedError()

    @action
    def off(self, args):
        """ Turn the device off """
        raise NotImplementedError()

    @action
    def toggle(self, args):
        """ Toggle the device status (on/off) """
        raise NotImplementedError()

    @action
    def status(self):
        """ Get the device state """
        raise NotImplementedError()


# vim:sw=4:ts=4:et:

