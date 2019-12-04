import enum
import textwrap

from xml.dom.minidom import parseString
import requests

from platypush.plugins import action
from platypush.plugins.switch import SwitchPlugin


class SwitchAction(enum.Enum):
    GET_STATE = 'GetBinaryState'
    SET_STATE = 'SetBinaryState'
    GET_NAME = 'GetFriendlyName'


class SwitchWemoPlugin(SwitchPlugin):
    """
    Plugin to control a Belkin WeMo smart switches
    (https://www.belkin.com/us/Products/home-automation/c/wemo-home-automation/)

    Requires:

        * **requests** (``pip install requests``)
    """

    _default_port = 49153

    def __init__(self, devices=None, **kwargs):
        """
        :param devices: List of IP addresses or name->address map containing the WeMo Switch devices to control.
            This plugin previously used ouimeaux for auto-discovery but it's been dropped because
            1. too slow 2. too heavy 3. auto-discovery failed too often.
        :type devices: list or dict
        """

        super().__init__(**kwargs)
        self._port = self._default_port
        if devices:
            self._devices = devices if isinstance(devices, dict) else \
                {addr: addr for addr in devices}
        else:
            self._devices = {}

        self._addresses = set(self._devices.values())

    @property
    def devices(self):
        """
        Get the list of available devices
        :returns: The list of devices.

        Example output::

            output = [
                    {
                        "ip": "192.168.1.123",
                        "name": "Switch 1",
                        "on": true,
                    },

                    {
                        # ...
                    }
                ]
        """

        return [
                self.status(device).output
                for device in self._devices.values()
        ]

    def _exec(self, device: str, action: SwitchAction, port: int = _default_port, value=None):
        if device not in self._addresses:
            try:
                device = self._devices[device]
            except KeyError:
                pass

        state_name = action.value[3:]

        response = requests.post(
            'http://{}:{}/upnp/control/basicevent1'.format(device, port),
            headers={
                'User-Agent': '',
                'Accept': '',
                'Content-Type': 'text/xml; charset="utf-8"',
                'SOAPACTION': '\"urn:Belkin:service:basicevent:1#{}\"'.format(action.value),
            },
            data=textwrap.dedent(
                '''
                <?xml version="1.0" encoding="utf-8"?>
                <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
                        s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                    <s:Body>
                        <u:{action} xmlns:u="urn:Belkin:service:basicevent:1">
                            <{state}>{value}</{state}>
                        </u:{action}
                    ></s:Body>
                </s:Envelope>
                '''.format(action=action.value, state=state_name,
                           value=value if value is not None else ''))
        )

        dom = parseString(response.text)
        return dom.getElementsByTagName(state_name).item(0).firstChild.data

    @action
    def status(self, device=None, *args, **kwargs):
        devices = {device: device} if device else self._devices.copy()

        ret = [
            {
                'id': addr,
                'ip': addr,
                'name': name if name != addr else self.get_name(addr).output,
                'on': self.get_state(addr).output,
            }
            for (name, addr) in self._devices.items()
        ]

        return ret[0] if device else ret

    @action
    def on(self, device: str, **kwargs):
        """
        Turn a switch on

        :param device: Device name or address
        """
        self._exec(device=device, action=SwitchAction.SET_STATE, value=1)
        return self.status(device)

    @action
    def off(self, device: str, **kwargs):
        """
        Turn a switch off

        :param device: Device name or address
        """
        self._exec(device=device, action=SwitchAction.SET_STATE, value=0)
        return self.status(device)

    @action
    def toggle(self, device: str, *args, **kwargs):
        """
        Toggle a device on/off state

        :param device: Device name or address
        """
        state = self.get_state(device).output
        return self.on(device) if not state else self.off(device)

    @action
    def get_state(self, device: str):
        """
        Get the on state of a device (True/False)

        :param device: Device name or address
        """
        state = self._exec(device=device, action=SwitchAction.GET_STATE)
        return bool(int(state))

    @action
    def get_name(self, device: str):
        """
        Get the friendly name of a device

        :param device: Device name or address
        """
        return self._exec(device=device, action=SwitchAction.GET_NAME)


# vim:sw=4:ts=4:et:
