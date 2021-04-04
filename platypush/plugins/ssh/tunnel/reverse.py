import logging
import threading
import select
import socket

from typing import Callable

logger = logging.getLogger(__name__)
should_run = {}


def handler(chan, local_port, host, port):
    key = local_port, host, port
    sock = socket.socket()
    try:
        sock.connect((host, port))
    except Exception as e:
        logger.warning('Forwarding request to {}:{} failed: {}'.format(host, port, e))
        return

    logger.info('Connected! Tunnel open {} -> {} -> {}'.format(
        chan.origin_addr, chan.getpeername(), (host, port)))

    while should_run.get(key):
        r, w, x = select.select([sock, chan], [], [])
        if sock in r:
            data = sock.recv(1024)
            if len(data) == 0:
                break
            chan.send(data)

        if chan in r:
            data = chan.recv(1024)
            if len(data) == 0:
                break
            sock.send(data)

    chan.close()
    sock.close()
    logger.info('Tunnel closed from {}'.format(chan.origin_addr))


def reverse_tunnel(server_port, remote_host, remote_port, transport, bind_addr='') -> Callable:
    def server():
        transport.request_port_forward(bind_addr, server_port)
        key = server_port, remote_host, remote_port
        should_run[key] = True

        while should_run.get(key):
            try:
                chan = transport.accept(1)
                assert chan is not None
            except Exception as e:
                logger.warning(e)
                continue

            thr = threading.Thread(
                target=handler, args=(chan, server_port, remote_host, remote_port))

            thr.setDaemon(True)
            thr.start()

    return server


def close_tunnel(server_port, remote_host, remote_port):
    key = server_port, remote_host, remote_port
    if key not in should_run:
        logger.info('No such active tunnel: {}:{}:{}'.format(server_port, remote_host, remote_port))

    del should_run[key]


# vim:sw=4:ts=4:et:
