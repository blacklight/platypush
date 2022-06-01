from typing import Optional, Collection, Mapping

from platypush.message.event import Event


class NotificationEvent(Event):
    """
    Event triggered when a message/notification is received on a subscribed
    channel.
    """

    def __init__(
        self,
        *args,
        id: str,
        topic: str,
        message: str,
        title: Optional[str] = None,
        priority: Optional[int] = None,
        time: Optional[int] = None,
        attachment: Optional[Mapping] = None,
        actions: Optional[Collection[Mapping]] = None,
        tags: Optional[Collection[str]] = None,
        url: Optional[str] = None,
        **kwargs
    ):
        """
        :param id: Message ID.
        :param topic: The topic where the message was received.
        :param message: Message body.
        :param title: Message title.
        :param priority: Message priority.
        :param time: Message UNIX timestamp.
        :param tags: Notification tags.
        :param url: URL spawned when the notification is clicked.
        :param actions: List of actions associated to the notification.
            Example:

            .. code-block:: json

                [
                    {
                        "action": "view",
                        "label": "Open portal",
                        "url": "https://home.nest.com/",
                        "clear": true
                    },
                    {
                        "action": "http",
                        "label": "Turn down",
                        "url": "https://api.nest.com/",
                        "method": "PUT",
                        "headers": {
                            "Authorization": "Bearer abcdef..."
                        },
                        "body": "{\\"temperature\\": 65}"
                    },
                    {
                        "action": "broadcast",
                        "label": "Take picture",
                        "intent": "com.myapp.TAKE_PICTURE_INTENT",
                        "extras": {
                            "camera": "front"
                        }
                    }
                ]

        :param attachment: Attachment metadata. Example:

            .. code-block:: json

                {
                  "name": "image.jpg",
                  "type": "image/jpeg",
                  "size": 30017,
                  "expires": 1654144935,
                  "url": "https://ntfy.example.com/file/01234abcd.jpg"
                }

        """
        super().__init__(
            *args,
            id=id,
            topic=topic,
            message=message,
            title=title,
            priority=priority,
            time=time,
            tags=tags,
            attachment=attachment,
            actions=actions,
            url=url,
            **kwargs
        )
