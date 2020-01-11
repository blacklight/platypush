from typing import Dict, Any

from platypush.plugins import Plugin, action


class NmapPlugin(Plugin):
    """
    Nmap network scanner/mapper integration.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @action
    def scan(self, hosts: str, ports: str, args: str, sudo: bool = False) -> Dict[str, Any]:
        """
        Perform a port scan towards a certain host or network.

        :param hosts: Host name/IP or IP subnet to scan (e.g. ``192.168.1.0/24``).
        :param ports: Port number, (comma-separated) list or (dash-separated) range to scan (default: all).
        :param args: Additional command line arguments for nmap.
        :param sudo: Execute nmap as root through sudo (default: ``False``).
        :return: Scan results, as an ip -> host map.
        """
        import nmap
        nm = nmap.PortScanner()
        return nm.scan(hosts=hosts, ports=ports, arguments=args, sudo=sudo).get('scan')


# vim:sw=4:ts=4:et:
