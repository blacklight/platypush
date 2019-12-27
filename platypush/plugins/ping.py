import re
import subprocess
import sys

from typing import Optional, List

from platypush.message.response.ping import PingResponse
from platypush.plugins import Plugin, action

PING_MATCHER = re.compile(
    r"(?P<min>\d+.\d+)/(?P<avg>\d+.\d+)/(?P<max>\d+.\d+)/(?P<mdev>\d+.\d+)"
)

PING_MATCHER_BUSYBOX = re.compile(
    r"(?P<min>\d+.\d+)/(?P<avg>\d+.\d+)/(?P<max>\d+.\d+)"
)

WIN32_PING_MATCHER = re.compile(r"(?P<min>\d+)ms.+(?P<max>\d+)ms.+(?P<avg>\d+)ms")


class PingPlugin(Plugin):
    """
    Perform ICMP network ping on remote hosts.
    """

    def __init__(self, executable: str = 'ping', count: int = 1, timeout: float = 5.0, **kwargs):
        """
        :param executable: Path to the ``ping`` executable. Default: the first ``ping`` executable found in PATH.
        :param count: Default number of packets that should be sent (default: 1).
        :param timeout: Default timeout before failing a ping request (default: 5 seconds).
        """

        super().__init__(**kwargs)
        self.executable = executable
        self.count = count
        self.timeout = timeout

    def _get_ping_cmd(self, host: str, count: int, timeout: float) -> List[str]:
        if sys.platform == 'win32':
            return [
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
    def ping(self, host: str, count: Optional[int] = None, timeout: Optional[float] = None) -> PingResponse:
        """
        Ping a remote host.
        :param host: Remote host IP or name
        :param count: Number of packets that should be sent (default: 1).
        :param timeout: Timeout before failing a ping request (default: 5 seconds).
        """

        count = count or self.count
        timeout = timeout or self.timeout

        pinger = subprocess.Popen(
            self._get_ping_cmd(host, count=count, timeout=timeout),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        try:
            out = pinger.communicate()
            if sys.platform == "win32":
                match = WIN32_PING_MATCHER.search(str(out).split("\n")[-1])
                min_val, avg_val, max_val = match.groups()
                mdev_val = None
            elif "max/" not in str(out):
                match = PING_MATCHER_BUSYBOX.search(str(out).split("\n")[-1])
                min_val, avg_val, max_val = match.groups()
                mdev_val = None
            else:
                match = PING_MATCHER.search(str(out).split("\n")[-1])
                min_val, avg_val, max_val, mdev_val = match.groups()

            return PingResponse(host=host, success=True, min=min_val, max=max_val, avg=avg_val, mdev=mdev_val)
        except (subprocess.CalledProcessError, AttributeError):
            return PingResponse(host=host, success=False)


# vim:sw=4:ts=4:et:
