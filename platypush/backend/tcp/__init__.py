import multiprocessing
import queue
import socket
import threading
from typing import Optional

from platypush.backend import Backend
from platypush.message import Message


class TcpBackend(Backend):
    """
    Backend that reads messages from a configured TCP port.

    You can use this backend to send messages to Platypush from any TCP client, for example:

      .. code-block:: bash

        $ echo '{"type": "request", "action": "shell.exec", "args": {"cmd": "ls /"}}' | nc localhost 1234

    .. warning:: Be **VERY** careful when exposing this backend to the Internet. Unlike the HTTP backend, this backend
        doesn't implement any authentication mechanisms, so anyone who can connect to the TCP port will be able to
        execute commands on your Platypush instance.

    """

    # Maximum length of a request to be processed
    _MAX_REQ_SIZE = 2048

    def __init__(self, port, bind_address=None, listen_queue=5, **kwargs):
        """
        :param port: TCP port number
        :type port: int

        :param bind_address: Specify a bind address if you want to hook the
            service to a specific interface (default: listen for any connections).
        :type bind_address: str

        :param listen_queue: Maximum number of queued connections (default: 5)
        :type listen_queue: int
        """

        super().__init__(name=self.__class__.__name__, **kwargs)

        self.port = port
        self.bind_address = bind_address or '0.0.0.0'
        self.listen_queue = listen_queue
        self._accept_queue = multiprocessing.Queue()
        self._srv: Optional[multiprocessing.Process] = None

    def _process_client(self, sock, address):
        def _f():
            processed_bytes = 0
            open_brackets = 0
            msg = b''
            prev_ch = None

            while not self.should_stop():
                if processed_bytes > self._MAX_REQ_SIZE:
                    self.logger.warning(
                        'Ignoring message longer than {} bytes from {}'.format(
                            self._MAX_REQ_SIZE, address[0]
                        )
                    )
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
            self.logger.info('Received request from %s: %s', msg, address[0])
            self.on_message(msg)

            response = self.get_message_response(msg)
            self.logger.info('Processing response on the TCP backend: %s', response)

            if response:
                sock.send(str(response).encode())

        def _f_wrapper():
            try:
                _f()
            finally:
                sock.close()

        threading.Thread(target=_f_wrapper, name='TCPListener').start()

    def _accept_process(self, serv_sock: socket.socket):
        while not self.should_stop():
            try:
                (sock, address) = serv_sock.accept()
                self._accept_queue.put((sock, address))
            except socket.timeout:
                continue

    def run(self):
        super().run()
        self.register_service(port=self.port)

        serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv_sock.bind((self.bind_address, self.port))
        serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serv_sock.settimeout(0.5)

        self.logger.info(
            'Initialized TCP backend on port %s with bind address %s',
            self.port,
            self.bind_address,
        )

        serv_sock.listen(self.listen_queue)
        self._srv = multiprocessing.Process(
            target=self._accept_process, args=(serv_sock,)
        )
        self._srv.start()

        while not self.should_stop():
            try:
                sock, address = self._accept_queue.get(timeout=1)
            except (socket.timeout, queue.Empty):
                continue

            self.logger.info('Accepted connection from client %s', address[0])
            self._process_client(sock, address)

        if self._srv:
            self._srv.kill()
            self._srv.join()
            self._srv = None

        self.logger.info('TCP backend terminated')


# vim:sw=4:ts=4:et:
