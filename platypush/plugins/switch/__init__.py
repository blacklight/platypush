from platypush.plugins import Plugin, action


class SwitchPlugin(Plugin):
    """
    Abstract class for interacting with switch devices
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @action
    def on(self, device, *args, **kwargs):
        """ Turn the device on """
        raise NotImplementedError()

    @action
    def off(self, device, *args, **kwargs):
        """ Turn the device off """
        raise NotImplementedError()

    @action
    def toggle(self, device, *args, **kwargs):
        """ Toggle the device status (on/off) """
        raise NotImplementedError()

    @action
    def status(self, device=None, *args, **kwargs):
        """ Get the status of a specified device or of all the configured devices (default)"""
        devices = self.devices
        if device:
            devices = [d for d in self.devices if d.get('id') == device or d.get('name') == device]
            if devices:
                return self.devices.pop(0)
            else:
                return None

        return devices

    @property
    def devices(self):
        raise NotImplementedError()


# vim:sw=4:ts=4:et:
