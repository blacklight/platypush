import asyncio
import json
import time

from typing import Optional, Collection

from websockets import connect as websocket_connect  # type: ignore
from websockets.exceptions import ConnectionClosed

from platypush.context import get_bus
from platypush.message.event.websocket import WebsocketMessageEvent
from platypush.plugins import AsyncRunnablePlugin, action
from platypush.utils import get_ssl_client_context


class WebsocketPlugin(AsyncRunnablePlugin):
    """
    Plugin to send and receive messages over websocket connections.

    Triggers:

        * :class:`platypush.message.event.websocket.WebsocketMessageEvent` when
            a message is received on a subscribed websocket.

    """

    def __init__(self, subscriptions: Optional[Collection[str]] = None, **kwargs):
        """
        :param subscriptions: List of websocket URLs that should be subscribed
            at startup, prefixed by ``ws://`` or ``wss://``.
        """
        super().__init__(**kwargs)
        self._subscriptions = subscriptions or []

    @property
    def loop(self):
        if not self._loop:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

        return self._loop

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
        timeout=None,
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
        :param timeout: If ``wait_response=True``, then ``timeout`` establishes
            how long we should wait for a response before returning (default:
            no timeout).
        :return: The received response if ``wait_response`` is set to True,
            otherwise nothing.
        """

        msg = self._parse_msg(msg)

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
                    self.logger.warning(
                        'Connection error to websocket %s: %s', url, err
                    )

                if wait_response:
                    messages = await self._recv(ws, num_messages=1, timeout=timeout)

                    if messages:
                        return self._parse_msg(messages[0])

        return asyncio.run_coroutine_threadsafe(send(), self.loop).result()

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
                return await self._recv(ws, timeout=timeout, num_messages=num_messages)

        return self.loop.call_soon_threadsafe(recv)

    async def _recv(self, ws, timeout: Optional[float] = 0, num_messages=0):
        messages = []
        time_start = time.time()
        time_end = time_start + timeout if timeout else 0
        url = 'ws{secure}://{host}:{port}{path}'.format(
            secure='s' if ws._secure else '',
            host=ws.remote_address[0],
            port=ws.remote_address[1],
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

    @property
    def _should_start_runner(self):
        return bool(self._subscriptions)

    @staticmethod
    def _parse_msg(msg):
        try:
            msg = json.dumps(msg)
        except Exception:
            pass

        return msg

    async def listen(self):
        async def _recv(url):
            async with websocket_connect(url) as ws:
                return await self._recv(ws)

        await asyncio.wait([_recv(url) for url in set(self._subscriptions)])

    @staticmethod
    def _get_ssl_context(
        url: str, ssl_cert=None, ssl_key=None, ssl_cafile=None, ssl_capath=None
    ):
        if url.startswith('wss://') or url.startswith('https://'):
            return get_ssl_client_context(
                ssl_cert=ssl_cert,
                ssl_key=ssl_key,
                ssl_cafile=ssl_cafile,
                ssl_capath=ssl_capath,
            )

        return None


# vim:sw=4:ts=4:et:
