from typing import List

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
    def switch_status(self, device=None):
        """ Get the status of a specified device or of all the configured devices (default)"""
        devices = self.switches
        if device:
            devices = [d for d in self.switches if d.get('id') == device or d.get('name') == device]
            if devices:
                return devices[0]
            else:
                return None

        return devices

    @action
    def status(self, device=None, *args, **kwargs):
        """
        Status function - if not overridden it calls :meth:`.switch_status`. You may want to override it if your plugin
        does not handle only switches.
        """
        return self.switch_status(device)

    @property
    def switches(self) -> List[dict]:
        """
        This property must be implemented by the derived classes and must return a dictionary in the following format:

            .. code-block:: json

                [
                    {
                        "name": "switch_1",
                        "on": true
                    },
                    {
                        "name": "switch_2",
                        "on": false
                    },
                ]

        ``name`` and ``on`` are the minimum set of attributes that should be returned for a switch, but more attributes
        can also be added.
        """
        raise NotImplementedError()


# vim:sw=4:ts=4:et:
