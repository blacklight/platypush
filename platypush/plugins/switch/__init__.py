from abc import ABC, abstractmethod
from typing import List, Union

from platypush.plugins import Plugin, action


class SwitchPlugin(Plugin, ABC):
    """
    Abstract class for interacting with switch devices
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @action
    @abstractmethod
    def on(self, device, *args, **kwargs):
        """ Turn the device on """
        raise NotImplementedError()

    @action
    @abstractmethod
    def off(self, device, *args, **kwargs):
        """ Turn the device off """
        raise NotImplementedError()

    @action
    @abstractmethod
    def toggle(self, device, *args, **kwargs):
        """ Toggle the device status (on/off) """
        raise NotImplementedError()

    @action
    def switch_status(self, device=None) -> Union[dict, List[dict]]:
        """
        Get the status of a specified device or of all the configured devices (default).

        :param device: Filter by device name or ID.
        :return: .. schema:: switch.SwitchStatusSchema(many=True)
        """
        devices = self.switches
        if device:
            devices = [d for d in self.switches if d.get('id') == device or d.get('name') == device]
            return devices[0] if devices else []

        return devices

    @action
    def status(self, device=None, *args, **kwargs) -> Union[dict, List[dict]]:
        """
        Get the status of all the devices, or filter by device name or ID (alias for :meth:`.switch_status`).

        :param device: Filter by device name or ID.
        :return: .. schema:: switch.SwitchStatusSchema(many=True)
        """
        return self.switch_status(device)

    @property
    @abstractmethod
    def switches(self) -> List[dict]:
        """
        :return: .. schema:: switch.SwitchStatusSchema(many=True)
        """
        raise NotImplementedError()


# vim:sw=4:ts=4:et:
