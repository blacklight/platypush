import enum
import re
import textwrap

from xml.dom.minidom import parseString
import requests


class SwitchAction(enum.Enum):
    GET_STATE = 'GetBinaryState'
    SET_STATE = 'SetBinaryState'
    GET_NAME = 'GetFriendlyName'


class WemoRunner:
    default_port = 49153

    @staticmethod
    def exec(device: str, action: SwitchAction, port: int = default_port, value=None):
        state_name = action.value[3:]

        response = requests.post(
            'http://{}:{}/upnp/control/basicevent1'.format(device, port),
            headers={
                'User-Agent': '',
                'Accept': '',
                'Content-Type': 'text/xml; charset="utf-8"',
                'SOAPACTION': '\"urn:Belkin:service:basicevent:1#{}\"'.format(action.value),
            },
            data=re.sub('\s+', ' ', textwrap.dedent(
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
                           value=value if value is not None else ''))))

        dom = parseString(response.text)
        return dom.getElementsByTagName(state_name).item(0).firstChild.data

    @classmethod
    def get_state(cls, device: str) -> bool:
        state = cls.exec(device=device, action=SwitchAction.GET_STATE)
        return bool(int(state))

    @classmethod
    def get_name(cls, device: str) -> str:
        name = cls.exec(device=device, action=SwitchAction.GET_NAME)
        return name

    @classmethod
    def on(cls, device):
        cls.exec(device=device, action=SwitchAction.SET_STATE, value=1)

    @classmethod
    def off(cls, device):
        cls.exec(device=device, action=SwitchAction.SET_STATE, value=0)

    @classmethod
    def toggle(cls, device):
        state = cls.get_state(device)
        cls.exec(device=device, action=SwitchAction.SET_STATE, value=int(not state))


# vim:sw=4:ts=4:et:
