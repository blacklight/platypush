import time

from typing import List, Tuple

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message.event.ping import HostUpEvent, HostDownEvent
from platypush.utils.workers import Worker, Workers


class PingBackend(Backend):
    """
    This backend allows you to ping multiple remote hosts at regular intervals.

    Triggers:

        - :class:`platypush.message.event.ping.HostDownEvent` if a host stops responding ping requests
        - :class:`platypush.message.event.ping.HostUpEvent` if a host starts responding ping requests

    """

    class Pinger(Worker):
        def __init__(self, *args, **kwargs):
            self.timeout = kwargs.pop('timeout')
            self.count = kwargs.pop('count')
            super().__init__(*args, **kwargs)

        def process(self, host: str) -> Tuple[str, bool]:
            pinger = get_plugin('ping')
            response = pinger.ping(host, timeout=self.timeout, count=self.count).output
            return host, response['success'] is True

    def __init__(self, hosts: List[str], timeout: float = 5.0, interval: float = 60.0, count: int = 1,  *args, **kwargs):
        """
        :param hosts: List of IP addresses or host names to monitor.
        :param timeout: Ping timeout.
        :param interval: Interval between two scans.
        :param count: Number of pings per host. A host will be considered down
            if all the ping requests fail.
        """

        super().__init__(*args, **kwargs)
        self.hosts = {h: None for h in hosts}
        self.timeout = timeout
        self.interval = interval
        self.count = count

    def run(self):
        super().run()
        self.logger.info('Starting ping backend with {} hosts to monitor'.format(len(self.hosts)))

        while not self.should_stop():
            workers = Workers(10, self.Pinger, timeout=self.timeout, count=self.count)

            with workers:
                for host in self.hosts.keys():
                    workers.put(host)

            for response in workers.responses:
                host, is_up = response
                if is_up != self.hosts[host]:
                    if is_up:
                        self.bus.post(HostUpEvent(host))
                    else:
                        self.bus.post(HostDownEvent(host))

                self.hosts[host] = is_up

            time.sleep(self.interval)


# vim:sw=4:ts=4:et:
