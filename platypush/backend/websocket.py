import asyncio
import websockets

from platypush.backend import Backend
from platypush.context import get_plugin, get_or_create_event_loop
from platypush.message import Message
from platypush.message.request import Request
from platypush.message.response import Response
from platypush.utils import get_ssl_server_context


class WebsocketBackend(Backend):
    """
    Backend to communicate messages over a websocket medium.

    Requires:

        * **websockets** (``pip install websockets``)
    """

    # Websocket client message recv timeout in seconds
    _websocket_client_timeout = 0

    # Default websocket service port
    _default_websocket_port = 8765

    def __init__(self, port=_default_websocket_port, bind_address='0.0.0.0',
                 ssl_cafile=None, ssl_capath=None, ssl_cert=None, ssl_key=None,
                 client_timeout=_websocket_client_timeout, **kwargs):
        """
        :param port: Listen port for the websocket server (default: 8765)
        :type port: int

        :param bind_address: Bind address for the websocket server (default: 0.0.0.0, listen for any IP connection)
        :type websocket_port: str

        :param ssl_cert: Path to the certificate file if you want to enable SSL (default: None)
        :type ssl_cert: str

        :param ssl_key: Path to the key file if you want to enable SSL (default: None)
        :type ssl_key: str

        :param ssl_cafile: Path to the certificate authority file if required by the SSL configuration (default: None)
        :type ssl_cafile: str

        :param ssl_capath: Path to the certificate authority directory if required by the SSL configuration (default: None)
        :type ssl_capath: str

        :param client_timeout: Timeout without any messages being received before closing a client connection. A zero timeout keeps the websocket open until an error occurs (default: 0, no timeout)
        :type ping_timeout: int
        """

        super().__init__(**kwargs)

        self.port = port
        self.bind_address = bind_address
        self.client_timeout = client_timeout
        self.active_websockets = set()

        self.ssl_context = get_ssl_server_context(ssl_cert=ssl_cert,
                                                  ssl_key=ssl_key,
                                                  ssl_cafile=ssl_cafile,
                                                  ssl_capath=ssl_capath) \
            if ssl_cert else None

    def send_message(self, msg, **kwargs):
        websocket = get_plugin('websocket')
        websocket_args = {}

        if self.ssl_context:
            url = 'wss://localhost:{}'.format(self.port)
            websocket_args['ssl'] = self.ssl_context
        else:
            url = 'ws://localhost:{}'.format(self.port)

        websocket.send(url=url, msg=msg, **websocket_args)

    def notify_web_clients(self, event):
        """ Notify all the connected web clients (over websocket) of a new event """
        async def send_event(websocket):
            try:
                await websocket.send(str(event))
            except Exception as e:
                self.logger.warning('Error on websocket send_event: {}'.format(e))

        loop = get_or_create_event_loop()
        active_websockets = self.active_websockets.copy()

        for ws in active_websockets:
            try:
                loop.run_until_complete(send_event(ws))
            except websockets.exceptions.ConnectionClosed:
                self.logger.info('Client connection lost')
                self.active_websockets.remove(ws)

    def run(self):
        super().run()
        self.register_service(port=self.port, name='ws')

        # noinspection PyUnusedLocal
        async def serve_client(websocket, path):
            self.active_websockets.add(websocket)
            self.logger.debug('New websocket connection from {}'.
                              format(websocket.remote_address[0]))

            try:
                while True:
                    if self.client_timeout:
                        msg = await asyncio.wait_for(websocket.recv(),
                                                     timeout=self.client_timeout)
                    else:
                        msg = await websocket.recv()

                    msg = Message.build(msg)
                    self.logger.info('Received message from {}: {}'.
                                     format(websocket.remote_address[0], msg))

                    self.on_message(msg)

                    if isinstance(msg, Request):
                        response = self.get_message_response(msg) or Response()
                        self.logger.info('Processing response on the websocket backend: {}'.
                                         format(response))

                        await websocket.send(str(response))

            except websockets.exceptions.ConnectionClosed as e:
                self.active_websockets.remove(websocket)
                self.logger.debug('Websocket client {} closed connection'.
                                  format(websocket.remote_address[0]))
            except asyncio.TimeoutError as e:
                self.active_websockets.remove(websocket)
                self.logger.debug('Websocket connection to {} timed out'.
                                  format(websocket.remote_address[0]))
            except Exception as e:
                self.logger.exception(e)

        self.logger.info('Initialized websocket backend on port {}, bind address: {}'.
                         format(self.port, self.bind_address))

        websocket_args = {}
        if self.ssl_context:
            websocket_args['ssl'] = self.ssl_context

        loop = get_or_create_event_loop()
        server = websockets.serve(serve_client, self.bind_address, self.port,
                                  **websocket_args)

        loop.run_until_complete(server)
        loop.run_forever()


# vim:sw=4:ts=4:et:
