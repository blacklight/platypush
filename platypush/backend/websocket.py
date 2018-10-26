import asyncio
import os
import ssl
import threading
import websockets

from platypush.backend import Backend
from platypush.context import get_plugin, get_or_create_event_loop
from platypush.message import Message
from platypush.message.request import Request


class WebsocketBackend(Backend):
    """
    Backend to communicate messages over a websocket medium.

    Requires:

        * **websockets** (``pip install websockets``)
    """

    def __init__(self, port=8765, bind_address='0.0.0.0', ssl_cert=None, **kwargs):
        """
        :param port: Listen port for the websocket server (default: 8765)
        :type port: int

        :param bind_address: Bind address for the websocket server (default: 0.0.0.0, listen for any IP connection)
        :type websocket_port: str

        :param ssl_cert: Path to the PEM certificate file if you want to enable SSL (default: None)
        :type ssl_cert: str
        """

        super().__init__(**kwargs)

        self.port = port
        self.bind_address = bind_address
        self.ssl_context = None

        if ssl_cert:
            self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            self.ssl_context.load_cert_chain(os.path.abspath(
                os.path.expanduser(ssl_cert)))


    def send_message(self, msg):
        websocket = get_plugin('websocket')
        websocket_args = {}

        if self.ssl_context:
            url = 'wss://localhost:{}'.format(self.port)
            websocket_args['ssl'] = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            websocket_args['ssl'].load_cert_chain(os.path.abspath(
                os.path.expanduser(ssl_cert)))
        else:
            url = 'ws://localhost:{}'.format(self.port)

        websocket.send(url=url, msg=msg, **websocket_args)


    def run(self):
        super().run()

        async def serve_client(websocket, path):
            self.logger.info('New websocket connection from {}'.
                             format(websocket.remote_address[0]))

            try:
                msg = await websocket.recv()
                msg = Message.build(msg)
                self.logger.info('Received message from {}: {}'.
                                 format(websocket.remote_address[0], msg))

                self.on_message(msg)

                if isinstance(msg, Request):
                    response = self.get_message_response(msg)

                    if response:
                        self.logger.info('Processing response on the websocket backend: {}'.
                                         format(response))

                        await websocket.send(str(response))
            except Exception as e:
                if isinstance(e, websockets.exceptions.ConnectionClosed):
                    self.logger.info('Websocket client {} closed connection'.
                                     format(websocket.remote_address[0]))
                else:
                    self.logger.exception(e)

        self.logger.info('Initialized websocket backend on port {}, bind address: {}'.
                         format(self.port, self.bind_address))

        websocket_args = {}
        if self.ssl_context:
            websocket_args['ssl'] = self.ssl_context

        loop = get_or_create_event_loop()
        server = websockets.serve(serve_client, self.bind_address, self.port, **websocket_args)
        loop.run_until_complete(server)
        loop.run_forever()


# vim:sw=4:ts=4:et:

