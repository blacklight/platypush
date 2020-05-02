import os
from typing import Optional, Tuple, Union, Dict

from samsungtvws import SamsungTVWS

from platypush.config import Config
from platypush.plugins import Plugin, action


class TvSamsungWsPlugin(Plugin):
    """
    Control a Samsung smart TV with Tizen OS over WiFi/ethernet. It should support any post-2016 Samsung with Tizen OS
    and enabled websocket-based connection.

    Requires:

        * **samsungtvws** (``pip install samsungtvws``)

    """

    workdir = os.path.join(Config.get('workdir'), 'samsungtvws')

    def __init__(self, host: Optional[str] = None, port: int = 8002, timeout: Optional[int] = 5, name='platypush',
                 token_file: str = os.path.join(workdir, 'token.txt'), **kwargs):
        """
        :param host: IP address or host name of the smart TV.
        :param port: Websocket port (default: 8002).
        :param timeout: Connection timeout in seconds (default: 5, specify 0 or None for no timeout).
        :param name: Name of the remote device (default: platypush).
        :param token_file: Path to the token file (default: ``~/.local/share/platypush/samsungtvws/token.txt``)
        """
        super().__init__(**kwargs)
        self.host = host
        self.port = port
        self.timeout = timeout
        self.name = name
        self.token_file = token_file
        self._connections: Dict[Tuple[host, port], SamsungTVWS] = {}
        os.makedirs(self.workdir, mode=0o700, exist_ok=True)

    def _get_host_and_port(self, host: Optional[str] = None, port: Optional[int] = None) -> Tuple[str, int]:
        host = host or self.host
        port = port or self.port
        assert host and port, 'No host/port specified'
        return host, port

    def connect(self, host: Optional[str] = None, port: Optional[int] = None) -> SamsungTVWS:
        host, port = self._get_host_and_port(host, port)
        if (host, port) not in self._connections:
            self._connections[(host, port)] = SamsungTVWS(host=host, port=port, token_file=self.token_file,
                                                          timeout=self.timeout, name=self.name)

        return self._connections[(host, port)]

    @action
    def power(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Send power on/off control to the device.

        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        tv.shortcuts().power()

    @action
    def volume_up(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Send volume up control to the device.

        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        tv.shortcuts().volume_up()

    @action
    def volume_down(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Send volume down control to the device.

        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        tv.shortcuts().volume_down()

    @action
    def back(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Send back key to the device.

        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        tv.shortcuts().back()

    @action
    def channel(self, channel: int, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Change to the selected channel.

        :param channel: Channel index.
        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        tv.shortcuts().channel(channel)

    @action
    def channel_up(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Send channel_up key to the device.

        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        tv.shortcuts().channel_up()

    @action
    def channel_down(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Send channel_down key to the device.

        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        tv.shortcuts().channel_down()

    @action
    def enter(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Send enter key to the device.

        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        tv.shortcuts().enter()

    @action
    def guide(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Send guide key to the device.

        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        tv.shortcuts().guide()

    @action
    def home(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Send home key to the device.

        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        tv.shortcuts().home()

    @action
    def info(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Send info key to the device.

        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        tv.shortcuts().info()

    @action
    def menu(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Send menu key to the device.

        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        tv.shortcuts().menu()

    @action
    def mute(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Send mute key to the device.

        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        tv.shortcuts().mute()

    @action
    def source(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Send source key to the device.

        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        tv.shortcuts().source()

    @action
    def tools(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Send tools key to the device.

        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        tv.shortcuts().tools()

    @action
    def up(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Send up key to the device.

        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        tv.shortcuts().up()

    @action
    def down(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Send down key to the device.

        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        tv.shortcuts().down()

    @action
    def left(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Send left key to the device.

        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        tv.shortcuts().left()

    @action
    def right(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Send right key to the device.

        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        tv.shortcuts().right()

    @action
    def blue(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Send blue key to the device.

        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        tv.shortcuts().blue()

    @action
    def green(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Send green key to the device.

        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        tv.shortcuts().green()

    @action
    def red(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Send red key to the device.

        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        tv.shortcuts().red()

    @action
    def yellow(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Send red key to the device.

        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        tv.shortcuts().yellow()

    @action
    def digit(self, digit: int, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Send a digit key to the device.

        :param digit: Digit to send.
        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        tv.shortcuts().digit(digit)

    @action
    def run_app(self, app_id: Union[int, str], host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Run an app by ID.

        :param app_id: App ID.
        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        tv.run_app(app_id)

    @action
    def list_apps(self, host: Optional[str] = None, port: Optional[int] = None) -> list:
        """
        Get the list of installed apps.

        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        return tv.app_list()

    @action
    def open_browser(self, url: str, host: Optional[str] = None, port: Optional[int] = None) -> None:
        """
        Open a URL in the browser.

        :param url: URL to open.
        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        return tv.open_browser(url)

    @action
    def device_info(self, host: Optional[str] = None, port: Optional[int] = None) -> dict:
        """
        Return the info of the device.

        :param host: Default host IP/name override.
        :param port: Default port override.
        """
        tv = self.connect(host, port)
        return tv.rest_device_info()


# vim:sw=4:ts=4:et:
