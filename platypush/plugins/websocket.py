import asyncio
import json
import os
import websockets

from platypush.context import get_or_create_event_loop
from platypush.message import Message
from platypush.plugins import Plugin, action
from platypush.utils import get_ssl_client_context


class WebsocketPlugin(Plugin):
    """
    Plugin to send messages over a websocket connection

    Requires:

        * **websockets** (``pip install websockets``)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @action
    def send(self, url, msg, ssl_cert=None, ssl_key=None, ssl_cafile=None,
             ssl_capath=None, *args, **kwargs):
        """
        Sends a message to a websocket.

        :param url: Websocket URL, e.g. ws://localhost:8765 or wss://localhost:8765
        :type topic: str

        :param msg: Message to be sent. It can be a list, a dict, or a Message object

        :param ssl_cert: Path to the SSL certificate to be used, if the SSL connection requires client authentication as well (default: None)
        :type ssl_cert: str

        :param ssl_key: Path to the SSL key to be used, if the SSL connection requires client authentication as well (default: None)
        :type ssl_key: str

        :param ssl_cafile: Path to the certificate authority file if required by the SSL configuration (default: None)
        :type ssl_cafile: str

        :param ssl_capath: Path to the certificate authority directory if required by the SSL configuration (default: None)
        :type ssl_capath: str
        """

        async def send():
            websocket_args = {}
            if ssl_cert:
                websocket_args['ssl'] = get_ssl_client_context(ssl_cert=ssl_cert,
                                                               ssl_key=ssl_key,
                                                               ssl_cafile=ssl_cafile,
                                                               ssl_capath=ssl_capath)

            async with websockets.connect(url, **websocket_args) as websocket:
                try:
                    await websocket.send(str(msg))
                except websockets.exceptions.ConnectionClosed:
                    self.logger.warning('Error on websocket {}: {}'.
                                        format(url, e))

        try: msg = json.dumps(msg)
        except: pass

        try: msg = Message.build(json.loads(msg))
        except: pass

        loop = get_or_create_event_loop()
        loop.run_until_complete(send())


# vim:sw=4:ts=4:et:

