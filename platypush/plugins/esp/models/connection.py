import enum
import re
import threading
from typing import Optional, Union

from platypush.utils import grouper


class Connection:
    """
    This class models the connection with an ESP8266/ESP32 device over its WebREPL websocket channel.
    """

    class State(enum.IntEnum):
        DISCONNECTED = 1
        CONNECTED = 2
        PASSWORD_REQUIRED = 3
        READY = 4
        SENDING_REQUEST = 5
        WAITING_ECHO = 6
        WAITING_RESPONSE = 7

    def __init__(self, host: str, port: int, connect_timeout: Optional[float] = None,
                 password: Optional[str] = None, ws=None):
        self.host = host
        self.port = port
        self.connect_timeout = connect_timeout
        self.password = password
        self.state = self.State.DISCONNECTED
        self.ws = ws
        self._connected = threading.Event()
        self._logged_in = threading.Event()
        self._echo_received = threading.Event()
        self._response_received = threading.Event()
        self._password_requested = False
        self._running_cmd = None
        self._received_echo = None
        self._received_response = None
        self._paste_header_received = False

    def send(self, msg: Union[str, bytes], wait_response: bool = True, timeout: Optional[float] = None):
        bufsize = 255

        msg = (msg
               .replace("\n", "\r\n")  # end of command in normal mode
               .replace("\\x01", "\x01")  # switch to raw mode
               .replace("\\x02", "\x02")  # switch to normal mode
               .replace("\\x03", "\x03")  # interrupt
               .replace("\\x04", "\x04")  # end of command in raw mode
               .encode())

        if not msg.endswith(b'\r\n'):
            msg += b'\r\n'
        if wait_response:
            # Enter PASTE mode and exit on end-of-message
            msg = b'\x05' + msg + b'\x04'

        if wait_response:
            self.state = self.State.SENDING_REQUEST
            self._running_cmd = msg.decode().strip()
            self._received_echo = ''

        self._response_received.clear()
        self._echo_received.clear()
        for chunk in grouper(bufsize, msg):
            self.ws.send(bytes(chunk))

        if wait_response:
            self.state = self.State.WAITING_ECHO
            echo_received = self._echo_received.wait(timeout=timeout)
            if not echo_received:
                self.on_timeout('No response echo received')

            self._paste_header_received = False
            response_received = self._response_received.wait(timeout=timeout)
            if not response_received:
                self.on_timeout('No response received')

            response = self._received_response
            self._received_response = None
            return response

    def on_connect(self):
        self.state = Connection.State.CONNECTED
        self._connected.set()

    def on_password_requested(self):
        self._password_requested = True
        self.state = Connection.State.PASSWORD_REQUIRED
        assert self.password, 'This device is protected by password and no password was provided'
        self.send(self.password, wait_response=False)

    def on_ready(self):
        self.state = Connection.State.READY
        self._logged_in.set()

    def on_close(self):
        self.state = self.State.DISCONNECTED
        self._connected.clear()
        self._logged_in.clear()
        self._password_requested = False
        self.ws = None

    def on_recv_echo(self, echo):
        def str_transform(s: str):
            s = s.replace('\x05', '').replace('\x04', '').replace('\r', '')
            s = re.sub('^[\s\r\n]+', '', s)
            s = re.sub('[\s\r\n]+$', '', s)
            return s

        if echo.endswith('\r\n=== ') and not self._paste_header_received:
            self._paste_header_received = True
            return

        if re.match('\s+>>>\s+', echo) \
                or re.match('\s+\.\.\.\s+', echo) \
                or re.match('\s+===\s+', echo):
            return

        self._received_echo += echo
        running_cmd = str_transform(self._running_cmd)
        received_echo = str_transform(self._received_echo)

        if running_cmd == received_echo:
            self._received_echo = None
            self.state = self.State.WAITING_RESPONSE
            self._echo_received.set()

    def close(self):
        # noinspection PyBroadException
        try:
            self.ws.close()
        except:
            pass

        self.on_close()

    def on_timeout(self, msg: str = ''):
        self.close()
        raise TimeoutError(msg)

    def append_response(self, response):
        if isinstance(response, bytes):
            response = response.decode()

        if not self._received_response:
            self._received_response = ''

        self._received_response += response

    def on_recv_response(self, response):
        self.append_response(response)
        self.state = self.State.READY
        self._received_response = self._received_response.strip()

        if self._received_response.startswith('=== '):
            # Strip PASTE mode output residual
            self._received_response = self._received_response[4:]
            self._received_response = self._received_response.strip()

        self._response_received.set()

    def wait_ready(self):
        connected = self._connected.wait(timeout=self.connect_timeout)
        if not connected:
            self.on_timeout('Connection timed out')

        logged_in = self._logged_in.wait(timeout=self.connect_timeout)
        if not logged_in:
            self.on_timeout('Log in timed out')


# vim:sw=4:ts=4:et:
