import enum
import logging
import queue
import os
import re
import threading
import websocket
from typing import Optional, Union

from platypush.utils import grouper


class Connection:
    """
    This class models the connection with an ESP8266/ESP32 device over its WebREPL websocket channel.
    """

    _file_transfer_buffer_size = 1024

    class State(enum.IntEnum):
        DISCONNECTED = 1
        CONNECTED = 2
        PASSWORD_REQUIRED = 3
        READY = 4
        SENDING_REQUEST = 5
        WAITING_ECHO = 6
        WAITING_RESPONSE = 7
        SENDING_FILE_TRANSFER_RESPONSE = 8
        WAITING_FILE_TRANSFER_RESPONSE = 9
        UPLOADING_FILE = 10
        DOWNLOADING_FILE = 11

    class FileRequestType(enum.IntEnum):
        UPLOAD = 1
        DOWNLOAD = 2

    def __init__(self, host: str, port: int, connect_timeout: Optional[float] = None,
                 password: Optional[str] = None, ws: Optional[websocket.WebSocketApp] = None):
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
        self._download_chunk_ready = threading.Event()
        self._file_transfer_request_ack_received = threading.Event()
        self._file_transfer_ack_received = threading.Event()
        self._file_transfer_request_successful = True
        self._file_transfer_successful = True
        self._downloaded_chunks = queue.Queue()
        self._password_requested = False
        self._running_cmd = None
        self._received_echo = None
        self._received_response = None
        self._paste_header_received = False
        self.logger = logging.getLogger('platypush:plugin:esp')

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

        if not wait_response:
            return

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

        # Replace \r\n serial end-of-line with \n
        self._received_response = self._received_response.replace('\r\n', '\n')

        # Notify the listeners
        self._response_received.set()

    def on_recv_file_transfer_response(self, response):
        self._file_transfer_request_successful = self._parse_file_transfer_response(response)
        self._file_transfer_request_ack_received.set()

    def on_file_transfer_completed(self, response):
        self._file_transfer_successful = self._parse_file_transfer_response(response)
        self._file_transfer_ack_received.set()

    def on_file_upload_start(self):
        self.logger.info('Starting file upload')
        self._file_transfer_successful = False
        self._file_transfer_ack_received.clear()
        self.state = self.State.UPLOADING_FILE

    def on_file_download_start(self):
        self.logger.info('Starting file download')
        self._file_transfer_successful = False
        self._downloaded_chunks = queue.Queue()
        self.state = self.State.DOWNLOADING_FILE
        self._file_transfer_ack_received.clear()
        self.ws.send(b'\x00', opcode=websocket.ABNF.OPCODE_BINARY)

    def on_chunk_received(self, data):
        size = data[0] | (data[1] << 8)
        data = data[2:]
        if len(data) != size:
            return

        self.logger.info('Received chunk of size {} (total size={})'.format(len(data), size))
        if size == 0:
            # End of file
            self.logger.info('File download completed')
            self._downloaded_chunks.put(None)
            self.on_file_download_completed()
        else:
            self._downloaded_chunks.put(data)
            self.ws.send(b'\x00', opcode=websocket.ABNF.OPCODE_BINARY)

        self._download_chunk_ready.set()
        self._download_chunk_ready.clear()

    def on_file_download_completed(self):
        self.state = self.State.READY

    def on_file_transfer_request(self):
        self.logger.info('Sending file transfer request')
        self._file_transfer_request_successful = False
        self._file_transfer_request_ack_received.clear()
        self.state = self.State.SENDING_FILE_TRANSFER_RESPONSE

    def get_downloaded_chunks(self, timeout: Optional[float] = None):
        while True:
            try:
                chunk = self._downloaded_chunks.get(timeout=timeout)
            except queue.Empty:
                self.on_timeout('File download timed out')

            if chunk is None:
                break

            yield chunk

    def wait_ready(self):
        connected = self._connected.wait(timeout=self.connect_timeout)
        if not connected:
            self.on_timeout('Connection timed out')

        logged_in = self._logged_in.wait(timeout=self.connect_timeout)
        if not logged_in:
            self.on_timeout('Log in timed out')

    def wait_file_request_ack_received(self, timeout):
        self.state = self.State.WAITING_FILE_TRANSFER_RESPONSE
        self._file_transfer_request_ack_received.wait(timeout=timeout)
        assert self._file_transfer_request_successful, 'File transfer request failed'
        self.logger.info('File transfer request acknowledged')

    def wait_file_transfer_completed(self, timeout):
        self._file_transfer_ack_received.wait(timeout)
        assert self._file_transfer_successful, 'File transfer failed'
        self.logger.info('File transfer completed')

    @staticmethod
    def _parse_file_transfer_response(response: bytes) -> bool:
        if not response or len(response) < 4:
            return False

        if response[0] == ord('W') and response[1] == ord('B'):
            return response[2] | response[3] << 8 == 0
        return False

    def _send_file_request(self, filename: str, request_type: FileRequestType, file_size: int = 0,
                           timeout: Optional[float] = None):
        self.on_file_transfer_request()

        # 2 + 1 + 1 + 8 + 4 + 2 + 64
        request = bytearray(82)

        # Protocol mode (file transfer) and request type (1=PUT, 2=GET)
        request[0] = ord('W')
        request[1] = ord('A')
        request[2] = request_type.value

        # File size encoding
        request[12] = file_size & 0xff
        request[13] = (file_size >> 8) & 0xff
        request[14] = (file_size >> 16) & 0xff
        request[15] = (file_size >> 24) & 0xff

        # File name length encoding
        request[16] = len(filename) & 0xff
        request[17] = (len(filename) >> 8) & 0xff

        # File name encoding
        for i in range(0, min(64, len(filename))):
            request[i+18] = ord(filename[i])

        self.ws.send(request, opcode=websocket.ABNF.OPCODE_BINARY)
        self.wait_file_request_ack_received(timeout=timeout)

    def _upload_file(self, f, timeout):
        self.on_file_upload_start()
        content = f.read(self._file_transfer_buffer_size)

        while content:
            self.ws.send(content, opcode=websocket.ABNF.OPCODE_BINARY)
            content = f.read(self._file_transfer_buffer_size)

        self.wait_file_transfer_completed(timeout=timeout)
        self.state = self.State.READY

    def _download_file(self, f, timeout):
        self.on_file_download_start()
        for chunk in self.get_downloaded_chunks(timeout=timeout):
            f.write(chunk)

        self.on_file_download_completed()

    def file_upload(self, source, destination, timeout):
        source = os.path.abspath(os.path.expanduser(source))
        destination = os.path.join(destination, os.path.basename(source)) if destination else os.path.basename(source)
        size = os.path.getsize(source)

        with open(source, 'rb') as f:
            self._send_file_request(destination, self.FileRequestType.UPLOAD, file_size=size, timeout=timeout)
            self._upload_file(f, timeout=timeout)

    def file_download(self, file, fd, timeout=None):
        self._send_file_request(file, request_type=self.FileRequestType.DOWNLOAD, timeout=timeout)
        self._download_file(fd, timeout=timeout)


# vim:sw=4:ts=4:et:
