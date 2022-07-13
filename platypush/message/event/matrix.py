from abc import ABC
from datetime import datetime
from typing import Dict, Any

from platypush.message.event import Event


class MatrixEvent(Event, ABC):
    """
    Base matrix event.
    """

    def __init__(
        self,
        *args,
        server_url: str,
        sender_id: str | None = None,
        sender_display_name: str | None = None,
        sender_avatar_url: str | None = None,
        room_id: str | None = None,
        room_name: str | None = None,
        room_topic: str | None = None,
        server_timestamp: datetime | None = None,
        **kwargs
    ):
        """
        :param server_url: Base server URL.
        :param sender_id: The event's sender ID.
        :param sender_display_name: The event's sender display name.
        :param sender_avatar_url: The event's sender avatar URL.
        :param room_id: Event room ID.
        :param room_name: The name of the room associated to the event.
        :param room_topic: The topic of the room associated to the event.
        :param server_timestamp: The server timestamp of the event.
        """
        evt_args: Dict[str, Any] = {
            'server_url': server_url,
        }

        if sender_id:
            evt_args['sender_id'] = sender_id
        if sender_display_name:
            evt_args['sender_display_name'] = sender_display_name
        if sender_avatar_url:
            evt_args['sender_avatar_url'] = sender_avatar_url
        if room_id:
            evt_args['room_id'] = room_id
        if room_name:
            evt_args['room_name'] = room_name
        if room_topic:
            evt_args['room_topic'] = room_topic
        if server_timestamp:
            evt_args['server_timestamp'] = server_timestamp

        super().__init__(*args, **evt_args, **kwargs)


class MatrixMessageEvent(MatrixEvent):
    """
    Event triggered when a message is received on a subscribed room.
    """

    def __init__(self, *args, body: str, **kwargs):
        """
        :param body: The body of the message.
        """
        super().__init__(*args, body=body, **kwargs)


class MatrixRoomJoinEvent(MatrixEvent):
    """
    Event triggered when a user joins a room.
    """


class MatrixRoomLeaveEvent(MatrixEvent):
    """
    Event triggered when a user leaves a room.
    """


class MatrixRoomInviteEvent(MatrixEvent):
    """
    Event triggered when a user is invited to a room.
    """


class MatrixRoomInviteMeEvent(MatrixEvent):
    """
    Event triggered when the currently logged in user is invited to a room.
    """


class MatrixRoomTopicChangeEvent(MatrixEvent):
    """
    Event triggered when the topic/title of a room changes.
    """

    def __init__(self, *args, topic: str, **kwargs):
        """
        :param topic: New room topic.
        """
        super().__init__(*args, topic=topic, **kwargs)
