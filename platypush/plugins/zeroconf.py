import queue
import time
from typing import List, Dict

import zeroconf
from zeroconf import Zeroconf, ServiceBrowser

from platypush.context import get_bus
from platypush.message.event.zeroconf import ZeroconfServiceAddedEvent, ZeroconfServiceRemovedEvent, \
    ZeroconfServiceUpdatedEvent, ZeroconfEvent
from platypush.plugins import Plugin, action


class ZeroconfListener(zeroconf.ServiceListener):
    def __init__(self, evt_queue: queue.Queue):
        super().__init__()
        self.evt_queue = evt_queue

    # noinspection PyUnusedLocal
    def add_service(self, zc: Zeroconf, type_: str, name: str):
        self.evt_queue.put(ZeroconfServiceAddedEvent(service_type=type_, service_name=name))

    # noinspection PyUnusedLocal
    def remove_service(self, zc: Zeroconf, type_: str, name: str):
        self.evt_queue.put(ZeroconfServiceRemovedEvent(service_type=type_, service_name=name))

    # noinspection PyUnusedLocal
    def update_service(self, zc: Zeroconf, type_: str, name: str):
        self.evt_queue.put(ZeroconfServiceUpdatedEvent(service_type=type_, service_name=name))


class ZeroconfPlugin(Plugin):
    """
    Plugin for Zeroconf services discovery.

    Requires:

        * **zeroconf** (``pip install zeroconf``)
    """

    @action
    def get_services(self, timeout: int = 5) -> List[str]:
        """
        Get the full list of services found on the network.

        :param timeout: Discovery timeout in seconds (default: 5).
        :return: List of the services as strings.
        """
        return list(zeroconf.ZeroconfServiceTypes.find(timeout=timeout))

    @action
    def discover_service(self, service: str, timeout: int = 5) -> Dict[str, List[str]]:
        """
        Find all the services matching the specified type.

        :param service: Service type (e.g. ``_http._tcp.local.``).
        :param timeout: Browser timeout in seconds (default: 5).
        :return: A ``service_type -> [service_names]`` mapping. Example::

            {
                "_platypush-http._tcp.local.": [
                    "host1._platypush-http._tcp.local.",
                    "host2._platypush-http._tcp.local."
                ],
                ...
            }

        """
        evt_queue = queue.Queue()
        zc = Zeroconf()
        listener = ZeroconfListener(evt_queue=evt_queue)
        browser = ServiceBrowser(zc, service, listener)
        discovery_start = time.time()
        services = {}

        try:
            while time.time() - discovery_start < timeout:
                to = discovery_start + timeout - time.time()
                try:
                    evt: ZeroconfEvent = evt_queue.get(block=True, timeout=to)
                    if isinstance(evt, ZeroconfServiceAddedEvent) or isinstance(evt, ZeroconfServiceUpdatedEvent):
                        if evt.service_type not in services:
                            services[evt.service_type] = set()

                        services[evt.service_type].add(evt.service_name)
                    elif isinstance(evt, ZeroconfServiceRemovedEvent):
                        if evt.service_type in services:
                            if evt.service_name in services[evt.service_type]:
                                services[evt.service_type].remove(evt.service_name)
                            if not services[evt.service_type]:
                                del services[evt.service_type]

                    get_bus().post(evt)
                except queue.Empty:
                    if not services:
                        self.logger.warning('No such service discovered: {}'.format(service))
        finally:
            browser.cancel()
            zc.close()

        return {
            type_: list(names)
            for type_, names in services.items()
        }


# vim:sw=4:ts=4:et:
