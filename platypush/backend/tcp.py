import socket
import threading

from platypush.backend import Backend
from platypush.message import Message
from platypush.utils import set_thread_name


class TcpBackend(Backend):
    """
    Backend that reads messages from a configured TCP port
    """

    # Maximum length of a request to be processed
    _MAX_REQ_SIZE = 2048

    def __init__(self, port, bind_address=None, listen_queue=5, *args, **kwargs):
        """
        :param port: TCP port number
        :type port: int

        :param bind_address: Specify a bind address if you want to hook the service to a specific interface (default: listen for any connections)
        :type bind_address: str

        :param listen_queue: Maximum number of queued connections (default: 5)
        :type listen_queue: int
        """

        super().__init__(*args, **kwargs)

        self.port = port
        self.bind_address = bind_address or '0.0.0.0'
        self.listen_queue = listen_queue

    def _process_client(self, sock, address):
        def _f():
            processed_bytes = 0
            open_brackets = 0
            msg = b''
            prev_ch = None

            while True:
                if processed_bytes > self._MAX_REQ_SIZE:
                    self.logger.warning('Ignoring message longer than {} bytes from {}'
                                        .format(self._MAX_REQ_SIZE, address[0]))
                    return

                ch = sock.recv(1)
                processed_bytes += 1

                if ch == b'':
                    break

                if ch == b'{' and prev_ch != b'\\':
                    open_brackets += 1

                if not open_brackets:
                    continue

                msg += ch

                if ch == b'}' and prev_ch != b'\\':
                    open_brackets -= 1

                if not open_brackets:
                    break

                prev_ch = ch

            if msg == b'':
                return

            msg = Message.build(msg)
            self.logger.info('Received request from {}: {}'.format(msg, address[0]))
            self.on_message(msg)

            response = self.get_message_response(msg)
            self.logger.info('Processing response on the TCP backend: {}'.format(response))

            if response:
                sock.send(str(response).encode())

        def _f_wrapper():
            set_thread_name('TCPListener')
            try:
                _f()
            finally:
                sock.close()

        threading.Thread(target=_f_wrapper, name='TCPListener').start()

    def run(self):
        super().run()
        self.register_service(port=self.port)

        serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv_sock.bind((self.bind_address, self.port))

        self.logger.info('Initialized TCP backend on port {} with bind address {}'.
                         format(self.port, self.bind_address))

        serv_sock.listen(self.listen_queue)

        while not self.should_stop():
            (sock, address) = serv_sock.accept()
            self.logger.info('Accepted connection from client {}'.format(address[0]))
            self._process_client(sock, address)


# vim:sw=4:ts=4:et:
