import queue
import socket
import time
from typing import List, Dict, Any, Optional, Union

from zeroconf import Zeroconf, ServiceInfo, ServiceBrowser, ServiceListener, ZeroconfServiceTypes

from platypush.context import get_bus
from platypush.message.event.zeroconf import ZeroconfServiceAddedEvent, ZeroconfServiceRemovedEvent, \
    ZeroconfServiceUpdatedEvent
from platypush.plugins import Plugin, action


class ZeroconfListener(ServiceListener):
    def __init__(self, evt_queue: queue.Queue):
        super().__init__()
        self.evt_queue = evt_queue

    @classmethod
    def get_service_info(cls, zc: Zeroconf, type_: str, name: str) -> dict:
        info = zc.get_service_info(type_, name)
        if not info:
            return {}

        return cls.parse_service_info(info)

    @staticmethod
    def parse_service_info(info: ServiceInfo) -> dict:
        return {
            'addresses': [socket.inet_ntoa(addr) for addr in info.addresses if info.addresses],
            'port': info.port,
            'host_ttl': info.host_ttl,
            'other_ttl': info.other_ttl,
            'priority': info.priority,
            'properties': {k.decode() if isinstance(k, bytes) else k: v.decode() if isinstance(v, bytes) else v
                           for k, v in info.properties.items()},
            'server': info.server,
            'weight': info.weight,
        }

    def add_service(self, zc: Zeroconf, type_: str, name: str):
        info = self.get_service_info(zc, type_, name)
        self.evt_queue.put(ZeroconfServiceAddedEvent(service_type=type_, service_name=name, service_info=info))

    def remove_service(self, zc: Zeroconf, type_: str, name: str):
        info = self.get_service_info(zc, type_, name)
        self.evt_queue.put(ZeroconfServiceRemovedEvent(service_type=type_, service_name=name, service_info=info))

    def update_service(self, zc: Zeroconf, type_: str, name: str):
        info = self.get_service_info(zc, type_, name)
        self.evt_queue.put(ZeroconfServiceUpdatedEvent(service_type=type_, service_name=name, service_info=info))


class ZeroconfPlugin(Plugin):
    """
    Plugin for Zeroconf services discovery.

    Triggers:

        * :class:`platypush.message.event.zeroconf.ZeroconfServiceAddedEvent` when a new service is discovered.
        * :class:`platypush.message.event.zeroconf.ZeroconfServiceUpdatedEvent` when a service is updated.
        * :class:`platypush.message.event.zeroconf.ZeroconfServiceRemovedEvent` when a service is removed.

    Requires:

        * **zeroconf** (``pip install zeroconf``)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._discovery_in_progress = False

    @action
    def get_services(self, timeout: int = 5) -> List[str]:
        """
        Get the full list of services found on the network.

        :param timeout: Discovery timeout in seconds (default: 5).
        :return: List of the services as strings.
        """
        return list(ZeroconfServiceTypes.find(timeout=timeout))

    @action
    def discover_service(self, service: Union[str, list], timeout: Optional[int] = 5) -> Dict[str, Any]:
        """
        Find all the services matching the specified type.

        :param service: Service type (e.g. ``_http._tcp.local.``) or list of service types.
        :param timeout: Browser timeout in seconds (default: 5). Specify None for no timeout - in such case the
            discovery will loop forever and generate events upon service changes.
        :return: A ``service_type -> [service_names]`` mapping. Example:

          .. code-block:: json

            {
                "host1._platypush-http._tcp.local.": {
                    "type": "_platypush-http._tcp.local.",
                    "name": "host1._platypush-http._tcp.local.",
                    "info": {
                        "addresses": ["192.168.1.11"],
                        "port": 8008,
                        "host_ttl": 120,
                        "other_ttl": 4500,
                        "priority": 0,
                        "properties": {
                            "name": "Platypush",
                            "vendor": "Platypush",
                            "version": "0.13.2"
                        },
                        "server": "host1._platypush-http._tcp.local.",
                        "weight": 0
                    }
                }
            }

        """
        assert not self._discovery_in_progress, 'A discovery process is already running'
        self._discovery_in_progress = True

        evt_queue = queue.Queue()
        zc = Zeroconf()
        listener = ZeroconfListener(evt_queue=evt_queue)
        discovery_start = time.time()
        services = {}
        browser = None

        try:
            browser = ServiceBrowser(zc, service, listener)

            while timeout and time.time() - discovery_start < timeout:
                to = discovery_start + timeout - time.time() if timeout else None
                try:
                    evt = evt_queue.get(block=True, timeout=to)
                    if isinstance(evt, ZeroconfServiceAddedEvent) or isinstance(evt, ZeroconfServiceUpdatedEvent):
                        services[evt.service_name] = {
                            'type': evt.service_type,
                            'name': evt.service_name,
                            'info': evt.service_info,
                        }
                    elif isinstance(evt, ZeroconfServiceRemovedEvent):
                        if evt.service_name in services:
                            del services[evt.service_name]

                    get_bus().post(evt)
                except queue.Empty:
                    if not services:
                        self.logger.warning('No such service discovered: {}'.format(service))
        finally:
            if browser:
                browser.cancel()
            zc.close()
            self._discovery_in_progress = False

        return services


# vim:sw=4:ts=4:et:
