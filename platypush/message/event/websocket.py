from typing import Any

from platypush.message.event import Event


class WebsocketMessageEvent(Event):
    """
    Event triggered when a message is receive on a subscribed websocket URL.
    """

    def __init__(self, *args, url: str, message: Any, **kwargs):
        """
        :param url: Websocket URL.
        :param message: The received message.
        """
        super().__init__(*args, url=url, message=message, **kwargs)
