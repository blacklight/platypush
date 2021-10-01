from typing import Optional

from platypush.message.event import Event


class GotifyEvent(Event):
    """
    Gotify base event.
    """


class GotifyMessageEvent(GotifyEvent):
    """
    Event triggered when a message is received on the Gotify instance.
    """
    def __init__(self, *args,
                 message: str,
                 title: Optional[str] = None,
                 priority: Optional[int] = None,
                 extras: Optional[dict] = None,
                 date: Optional[str] = None,
                 id: Optional[int] = None,
                 appid: Optional[int] = None,
                 **kwargs):
        """
        :param message: Message body.
        :param title: Message title.
        :param priority: Message priority.
        :param extras: Message extra payload.
        :param date: Delivery datetime.
        :param id: Message ID.
        :param appid: ID of the sender application.
        """
        super().__init__(
            *args,
            message=message,
            title=title,
            priority=priority,
            extras=extras,
            date=date,
            id=id,
            appid=appid,
            **kwargs
        )
