from datetime import datetime
from typing import Dict, Any

from platypush.message.event import Event


class MatrixEvent(Event):
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


class MatrixSyncEvent(MatrixEvent):
    """
    Event triggered when the startup synchronization has been completed and the
    plugin is ready to use.
    """


class MatrixMessageEvent(MatrixEvent):
    """
    Event triggered when a message is received on a subscribed room.
    """

    def __init__(
        self,
        *args,
        body: str = '',
        url: str | None = None,
        thumbnail_url: str | None = None,
        mimetype: str | None = None,
        formatted_body: str | None = None,
        format: str | None = None,
        **kwargs
    ):
        """
        :param body: The body of the message.
        :param url: The URL of the media file, if the message includes media.
        :param thumbnail_url: The URL of the thumbnail, if the message includes media.
        :param mimetype: The MIME type of the media file, if the message includes media.
        :param formatted_body: The formatted body, if ``format`` is specified.
        :param format: The format of the message (e.g. ``html`` or ``markdown``).
        """
        super().__init__(
            *args,
            body=body,
            url=url,
            thumbnail_url=thumbnail_url,
            mimetype=mimetype,
            formatted_body=formatted_body,
            format=format,
            **kwargs
        )


class MatrixMessageImageEvent(MatrixEvent):
    """
    Event triggered when a message containing an image is received.
    """


class MatrixMessageFileEvent(MatrixEvent):
    """
    Event triggered when a message containing a generic file is received.
    """


class MatrixMessageAudioEvent(MatrixEvent):
    """
    Event triggered when a message containing an audio file is received.
    """


class MatrixMessageVideoEvent(MatrixEvent):
    """
    Event triggered when a message containing a video file is received.
    """


class MatrixReactionEvent(MatrixEvent):
    """
    Event triggered when a user submits a reaction to an event.
    """

    def __init__(self, *args, in_response_to_event_id: str, **kwargs):
        """
        :param in_response_to_event_id: The ID of the URL related to the reaction.
        """
        super().__init__(
            *args, in_response_to_event_id=in_response_to_event_id, **kwargs
        )


class MatrixEncryptedMessageEvent(MatrixMessageEvent):
    """
    Event triggered when a message is received but the client doesn't
    have the E2E keys to decrypt it, or encryption has not been enabled.
    """


class MatrixCallEvent(MatrixEvent):
    """
    Base class for Matrix call events.
    """

    def __init__(
        self, *args, call_id: str, version: int, sdp: str | None = None, **kwargs
    ):
        """
        :param call_id: The unique ID of the call.
        :param version: An increasing integer representing the version of the call.
        :param sdp: SDP text of the session description.
        """
        super().__init__(*args, call_id=call_id, version=version, sdp=sdp, **kwargs)


class MatrixCallInviteEvent(MatrixCallEvent):
    """
    Event triggered when the user is invited to a call.
    """

    def __init__(self, *args, invite_validity: float | None = None, **kwargs):
        """
        :param invite_validity: For how long the invite will be valid, in seconds.
        :param sdp: SDP text of the session description.
        """
        super().__init__(*args, invite_validity=invite_validity, **kwargs)


class MatrixCallAnswerEvent(MatrixCallEvent):
    """
    Event triggered by the callee when they wish to answer the call.
    """


class MatrixCallHangupEvent(MatrixCallEvent):
    """
    Event triggered when a participant in the call exists.
    """


class MatrixRoomCreatedEvent(MatrixEvent):
    """
    Event triggered when a room is created.
    """


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
    Event triggered when the user is invited to a room.
    """


class MatrixRoomTopicChangedEvent(MatrixEvent):
    """
    Event triggered when the topic/title of a room changes.
    """

    def __init__(self, *args, topic: str, **kwargs):
        """
        :param topic: New room topic.
        """
        super().__init__(*args, topic=topic, **kwargs)


class MatrixRoomTypingStartEvent(MatrixEvent):
    """
    Event triggered when a user in a room starts typing.
    """


class MatrixRoomTypingStopEvent(MatrixEvent):
    """
    Event triggered when a user in a room stops typing.
    """


class MatrixRoomSeenReceiptEvent(MatrixEvent):
    """
    Event triggered when the last message seen by a user in a room is updated.
    """


class MatrixUserPresenceEvent(MatrixEvent):
    """
    Event triggered when a user comes online or goes offline.
    """

    def __init__(self, *args, is_active: bool, last_active: datetime | None, **kwargs):
        """
        :param is_active: True if the user is currently online.
        :param topic: When the user was last active.
        """
        super().__init__(*args, is_active=is_active, last_active=last_active, **kwargs)
