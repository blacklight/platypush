import logging
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from typing import Collection, Dict, Iterable, Optional, List

from platypush.entities import EntityManager
from platypush.entities.ping import PingHost
from platypush.message.event.ping import HostUpEvent, HostDownEvent, PingResponseEvent
from platypush.plugins import RunnablePlugin, action
from platypush.schemas.ping import PingResponseSchema

PING_MATCHER = re.compile(
    r"(?P<min>\d+.\d+)/(?P<avg>\d+.\d+)/(?P<max>\d+.\d+)/(?P<mdev>\d+.\d+)"
)

PING_MATCHER_BUSYBOX = re.compile(r"(?P<min>\d+.\d+)/(?P<avg>\d+.\d+)/(?P<max>\d+.\d+)")

WIN32_PING_MATCHER = re.compile(r"(?P<min>\d+)ms.+(?P<max>\d+)ms.+(?P<avg>\d+)ms")


def ping(host: str, ping_cmd: List[str], logger: logging.Logger) -> dict:
    out = None
    pinger = None
    err_response = dict(
        PingResponseSchema().dump(
            {
                "host": host,
                "success": False,
            }
        )
    )

    try:
        with subprocess.Popen(
            ping_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) as pinger:
            out = pinger.communicate()
            if sys.platform == "win32":
                match = WIN32_PING_MATCHER.search(str(out).rsplit("\n", maxsplit=1)[-1])
                min_val, avg_val, max_val = match.groups()
                mdev_val = None
            elif "max/" not in str(out):
                match = PING_MATCHER_BUSYBOX.search(
                    str(out).rsplit("\n", maxsplit=1)[-1]
                )
                assert match is not None, out
                min_val, avg_val, max_val = match.groups()
                mdev_val = None
            else:
                match = PING_MATCHER.search(str(out).rsplit("\n", maxsplit=1)[-1])
                assert match is not None, out
                min_val, avg_val, max_val, mdev_val = match.groups()

            return dict(
                PingResponseSchema().dump(
                    {
                        "host": host,
                        "success": True,
                        "min": float(min_val),
                        "max": float(max_val),
                        "avg": float(avg_val),
                        "mdev": float(mdev_val) if mdev_val is not None else None,
                    }
                )
            )
    except Exception as e:
        err = (
            '\n'.join(line.decode().strip() for line in out)
            if isinstance(out, (tuple, list))
            else str(e)
        )

        logger.warning("Error while pinging host %s: %s", host, err)
        if pinger and pinger.poll() is None:
            pinger.kill()
            pinger.wait()

        return err_response


class PingPlugin(RunnablePlugin, EntityManager):
    """
    This integration allows you to:

        - Programmatic ping a remote host.
        - Monitor the status of a remote host.
    """

    def __init__(
        self,
        executable: str = 'ping',
        count: int = 1,
        timeout: float = 5.0,
        hosts: Optional[List[str]] = None,
        poll_interval: float = 20.0,
        **kwargs,
    ):
        """
        :param executable: Path to the ``ping`` executable. Default: the first ``ping`` executable found in PATH.
        :param count: Default number of packets that should be sent (default: 1).
        :param timeout: Default timeout before failing a ping request (default: 5 seconds).
        :param hosts: List of hosts to monitor. If not specified then no hosts will be monitored.
        :param poll_interval: How often the hosts should be monitored (default: 10 seconds).
        """

        super().__init__(poll_interval=poll_interval, **kwargs)
        self.executable = executable
        self.count = count
        self.timeout = timeout
        self.hosts: Dict[str, Optional[dict]] = {h: None for h in (hosts or [])}

    def _get_ping_cmd(self, host: str, count: int, timeout: float) -> List[str]:
        if sys.platform == 'win32':
            return [  # noqa
                self.executable,
                '-n',
                str(count or self.count),
                '-w',
                str((timeout or self.timeout) * 1000),
                host,
            ]

        return [
            self.executable,
            '-n',
            '-q',
            '-c',
            str(count or self.count),
            '-W',
            str(timeout or self.timeout),
            host,
        ]

    @action
    def ping(
        self, host: str, count: Optional[int] = None, timeout: Optional[float] = None
    ) -> dict:
        """
        Ping a remote host.

        :param host: Remote host IP or name
        :param count: Overrides the configured number of packets that should be
            sent (default: 1).
        :param timeout: Overrides the configured timeout before failing a ping
            request (default: 5 seconds).
        :return: .. schema:: ping.PingResponseSchema
        """
        return self._ping(host=host, count=count, timeout=timeout)

    def _ping(
        self, host: str, count: Optional[int] = None, timeout: Optional[float] = None
    ) -> dict:
        return ping(
            host=host,
            ping_cmd=self._get_ping_cmd(
                host=host, count=count or self.count, timeout=timeout or self.timeout
            ),
            logger=self.logger,
        )

    def _process_ping_result(self, result: dict):
        host = result.get("host")
        if host is None:
            return

        success = result.get("success")
        if success is None:
            return

        prev_result = self.hosts.get(host)
        if success:
            if not (prev_result and prev_result.get("success")):
                self._bus.post(HostUpEvent(host=host))

            self._bus.post(PingResponseEvent(**result))
            self.hosts[host] = result
        else:
            if not prev_result or prev_result.get("success"):
                self._bus.post(HostDownEvent(host=host))
            self.hosts[host] = result

    @action
    def status(self) -> Collection[PingHost]:
        """
        Get the status of the monitored hosts.
        :return: Dictionary of monitored hosts and their status.
        """
        return self.publish_entities()

    def publish_entities(self, *_, **__) -> Collection[PingHost]:
        return super().publish_entities(self.hosts.values())

    def transform_entities(
        self, entities: Collection[Optional[dict]], **_
    ) -> Iterable[PingHost]:
        return super().transform_entities(
            [
                PingHost(
                    id=status.get("host"),
                    name=status.get("host"),
                    reachable=status.get("success"),
                    min=status.get("min"),
                    max=status.get("max"),
                    avg=status.get("avg"),
                )
                for status in entities
                if status
            ]
        )

    def main(self):
        # Don't start the thread if no monitored hosts are configured
        if not self.hosts:
            self.wait_stop()
            return

        while not self.should_stop():
            try:
                with ProcessPoolExecutor() as executor:
                    for result in executor.map(
                        ping,
                        self.hosts.keys(),
                        [
                            self._get_ping_cmd(h, self.count, self.timeout)
                            for h in self.hosts.keys()
                        ],
                        [self.logger] * len(self.hosts),
                    ):
                        self._process_ping_result(result)
            except (KeyboardInterrupt, BrokenProcessPool):
                break
            except Exception as e:
                self.logger.warning("Error while pinging hosts: %s", e)
                self.logger.exception(e)
            finally:
                self.publish_entities()
                self.wait_stop(self.poll_interval)


# vim:sw=4:ts=4:et:
