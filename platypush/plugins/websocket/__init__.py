import asyncio
import json
import time

from websockets import connect as websocket_connect
from websockets.exceptions import ConnectionClosed

from platypush.context import get_or_create_event_loop, get_bus
from platypush.message.event.websocket import WebsocketMessageEvent
from platypush.plugins import Plugin, action
from platypush.utils import get_ssl_client_context


class WebsocketPlugin(Plugin):
    """
    Plugin to send messages over a websocket connection.

    Triggers:

        * :class:`platypush.message.event.websocket.WebsocketMessageEvent` when
            a message is received on a subscribed websocket.

    """

    @action
    def send(
        self,
        url: str,
        msg,
        ssl_cert=None,
        ssl_key=None,
        ssl_cafile=None,
        ssl_capath=None,
        wait_response=False,
    ):
        """
        Sends a message to a websocket.

        :param url: Websocket URL, e.g. ws://localhost:8765 or wss://localhost:8765
        :param msg: Message to be sent. It can be a list, a dict, or a Message object
        :param ssl_cert: Path to the SSL certificate to be used, if the SSL
            connection requires client authentication as well (default: None)
        :param ssl_key: Path to the SSL key to be used, if the SSL connection
            requires client authentication as well (default: None)
        :param ssl_cafile: Path to the certificate authority file if required
            by the SSL configuration (default: None)
        :param ssl_capath: Path to the certificate authority directory if
            required by the SSL configuration (default: None)
        :param wait_response: Set to True if you expect a response to the
            delivered message.
        :return: The received response if ``wait_response`` is set to True,
            otherwise nothing.
        """

        async def send():
            websocket_args = {
                'ssl': self._get_ssl_context(
                    url,
                    ssl_cert=ssl_cert,
                    ssl_key=ssl_key,
                    ssl_cafile=ssl_cafile,
                    ssl_capath=ssl_capath,
                )
            }

            async with websocket_connect(url, **websocket_args) as ws:
                try:
                    await ws.send(str(msg))
                except ConnectionClosed as err:
                    self.logger.warning('Error on websocket %s: %s', url, err)

                if wait_response:
                    messages = await self._ws_recv(ws, num_messages=1)
                    if messages:
                        return self._parse_msg(messages[0])

        msg = self._parse_msg(msg)
        loop = get_or_create_event_loop()
        return loop.run_until_complete(send())

    @action
    def recv(
        self,
        url: str,
        ssl_cert=None,
        ssl_key=None,
        ssl_cafile=None,
        ssl_capath=None,
        num_messages=0,
        timeout=0,
    ):
        """
        Receive one or more messages from a websocket.

        A :class:`platypush.message.event.websocket.WebsocketMessageEvent`
        event will be triggered whenever a new message is received.

        :param url: Websocket URL, e.g. ws://localhost:8765 or wss://localhost:8765
        :param ssl_cert: Path to the SSL certificate to be used, if the SSL
            connection requires client authentication as well (default: None)
        :param ssl_key: Path to the SSL key to be used, if the SSL connection
            requires client authentication as well (default: None)
        :param ssl_cafile: Path to the certificate authority file if required
            by the SSL configuration (default: None)
        :param ssl_capath: Path to the certificate authority directory if
            required by the SSL configuration (default: None)
        :param num_messages: Exit after receiving this number of messages.
            Default: 0, receive forever.
        :param timeout: Message receive timeout in seconds. Default: 0 - no timeout.
        :return: A list with the messages that have been received, unless
            ``num_messages`` is set to 0 or ``None``.
        """

        async def recv():
            websocket_args = {
                'ssl': self._get_ssl_context(
                    url,
                    ssl_cert=ssl_cert,
                    ssl_key=ssl_key,
                    ssl_cafile=ssl_cafile,
                    ssl_capath=ssl_capath,
                )
            }

            async with websocket_connect(url, **websocket_args) as ws:
                return await self._ws_recv(
                    ws, timeout=timeout, num_messages=num_messages
                )

        loop = get_or_create_event_loop()
        return loop.run_until_complete(recv())

    async def _ws_recv(self, ws, timeout=0, num_messages=0):
        messages = []
        time_start = time.time()
        time_end = time_start + timeout if timeout else 0
        url = 'ws{secure}://{host}:{port}{path}'.format(
            secure='s' if ws.secure else '',
            host=ws.host,
            port=ws.port,
            path=ws.path,
        )

        while (not num_messages) or (len(messages) < num_messages):
            msg = None
            err = None
            remaining_timeout = time_end - time.time() if time_end else None

            try:
                msg = await asyncio.wait_for(ws.recv(), remaining_timeout)
            except (ConnectionClosed, asyncio.exceptions.TimeoutError) as e:
                err = e
                self.logger.warning('Error on websocket %s: %s', url, e)

            if isinstance(err, ConnectionClosed) or (
                time_end and time.time() > time_end
            ):
                break

            if msg is None:
                continue

            msg = self._parse_msg(msg)
            messages.append(msg)
            get_bus().post(WebsocketMessageEvent(url=url, message=msg))

        return messages

    @staticmethod
    def _parse_msg(msg):
        try:
            msg = json.dumps(msg)
        except Exception:
            pass

        return msg

    @staticmethod
    def _get_ssl_context(
        url: str, ssl_cert=None, ssl_key=None, ssl_cafile=None, ssl_capath=None
    ):
        if url.startswith('wss://'):
            return get_ssl_client_context(
                ssl_cert=ssl_cert,
                ssl_key=ssl_key,
                ssl_cafile=ssl_cafile,
                ssl_capath=ssl_capath,
            )

        return None


# vim:sw=4:ts=4:et:
