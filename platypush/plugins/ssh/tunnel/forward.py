import logging
import select
import socketserver
from typing import Optional

from paramiko.transport import Transport


class ForwardServer(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


class Handler(socketserver.BaseRequestHandler):
    ssh_transport: Optional[Transport] = None
    chain_host: Optional[str] = None
    chain_port: Optional[int] = None
    logger = logging.Logger(__name__)

    def handle(self):
        try:
            chan = self.ssh_transport.open_channel(
                "direct-tcpip",
                (self.chain_host, self.chain_port),
                self.request.getpeername(),
            )
        except Exception as e:
            self.logger.warning('Incoming request to {host}:{port} failed: {error}'.format(
                host=self.chain_host, port=self.chain_port, error=repr(e)))
            return

        if chan is None:
            self.logger.warning('Incoming request to {host}:{port} was rejected by the SSH server'.format(
                host=self.chain_host, port=self.chain_port))
            return

        self.logger.info('Connected! Tunnel open {} -> {} -> {}'.format(
            self.request.getpeername(),
            chan.getpeername(),
            (self.chain_host, self.chain_port),
        ))

        while True:
            r, w, x = select.select([self.request, chan], [], [])
            if self.request in r:
                data = self.request.recv(1024)
                if len(data) == 0:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0:
                    break
                self.request.send(data)

        peer = self.request.getpeername()
        chan.close()
        self.request.close()
        self.logger.info('Tunnel closed from {}'.format(peer))


def forward_tunnel(local_port, remote_host, remote_port, transport, bind_addr='') -> ForwardServer:
    class SubHandler(Handler):
        ssh_transport = transport
        chain_host = remote_host
        chain_port = remote_port

    return ForwardServer((bind_addr, local_port), SubHandler)


# vim:sw=4:ts=4:et:
