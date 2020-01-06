from typing import Optional, Dict

from platypush.plugins import Plugin, action


class GraphitePlugin(Plugin):
    """
    Plugin for sending data to a Graphite instance.
    """

    def __init__(self, host: str = 'localhost', port: int = 2003, timeout: int = 5, **kwargs):
        """
        :param host: Default Graphite host (default: 'localhost').
        :param port: Default Graphite port (default: 2003).
        :param timeout: Communication timeout in seconds (default: 5).
        """
        super().__init__(**kwargs)
        self.host = host
        self.port = port
        self.timeout = timeout

    @action
    def send(self,
             metric: str,
             value,
             host: Optional[str] = None,
             port: Optional[int] = None,
             timeout: Optional[int] = None,
             tags: Optional[Dict[str, str]] = None,
             prefix: str = '',
             protocol: str = 'tcp'):
        """
        Send data to a Graphite instance.

        :param metric: Metric name.
        :param value: Value to be sent.
        :param host: Graphite host (default: default configured ``host``).
        :param port: Graphite port (default: default configured ``port``).
        :param tags: Map of tags for the metric.
        :param prefix: Metric prefix name (default: empty string).
        :param protocol: Communication protocol - possible values: 'tcp', 'udp' (default: 'tcp').
        """
        import graphyte

        host = host or self.host
        port = port or self.port
        tags = tags or {}
        protocol = protocol.lower()

        graphyte.init(host, port=port, prefix=prefix, protocol=protocol, timeout=timeout or self.timeout)
        graphyte.send(metric, value, tags=tags)


# vim:sw=4:ts=4:et:
