from typing import Optional

from platypush.message import Mapping


class EspWifiScanResult(Mapping):
    def __init__(self,
                 essid: str,
                 bssid: str,
                 channel: int,
                 rssi: int,
                 auth_mode: int,
                 hidden: bool,
                 *args,
                 **kwargs):
        self.essid = essid
        self.bssid = bssid
        self.channel = channel
        self.rssi = rssi
        self.auth_mode = auth_mode
        self.hidden = hidden
        super().__init__(*args, **dict(self), **kwargs)


class EspWifiConfigResult(Mapping):
    def __init__(self,
                 ip: str,
                 netmask: str,
                 gateway: str,
                 dns: str,
                 mac: str,
                 active: bool,
                 essid: Optional[str] = None,
                 channel: Optional[int] = None,
                 hidden: Optional[bool] = None,
                 *args,
                 **kwargs):
        self.ip = ip
        self.netmask = netmask
        self.gateway = gateway
        self.dns = dns
        self.mac = mac
        self.active = active
        self.essid = essid
        self.channel = channel
        self.hidden = hidden
        super().__init__(*args, **dict(self), **kwargs)


# vim:sw=4:ts=4:et:
