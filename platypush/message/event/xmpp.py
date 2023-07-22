from abc import ABC
from typing import Iterable, Optional, Union

from platypush.message.event import Event


class XmppEvent(Event, ABC):
    """
    Base class for XMPP events.
    """

    def __init__(self, *args, client_jabber_id: str, **kwargs):
        """
        :param client_jabber_id: The Jabber ID associated to the client connection.
        """
        super().__init__(*args, client_jabber_id=client_jabber_id, **kwargs)


class XmppUserEvent(XmppEvent, ABC):
    """
    Base class for XMPP user events.
    """

    def __init__(self, *args, user_id: str, jid: Optional[str] = None, **kwargs):
        """
        :param user_id: User ID.
        :param jid: The full Jabber ID of the user, if the visibility of the
            full ID including the client identifier is available.
        """
        jid = jid or user_id
        super().__init__(*args, user_id=user_id, jid=jid, **kwargs)


class XmppRoomEvent(XmppEvent, ABC):
    """
    Base class for XMPP room events.
    """

    def __init__(self, *args, room_id: str, **kwargs):
        """
        :param room_id: Room ID.
        """
        super().__init__(*args, room_id=room_id, **kwargs)


class XmppConversationEvent(XmppEvent, ABC):
    """
    Base class for XMPP p2p conversation events.
    """

    def __init__(self, *args, conversation_id: str, **kwargs):
        """
        :param conversation_id: Conversation ID.
        """
        super().__init__(*args, conversation_id=conversation_id, **kwargs)


class XmppRoomOccupantEvent(XmppRoomEvent, XmppUserEvent, ABC):
    """
    Base class for XMPP events about room members.
    """

    def __init__(self, *args, is_self: bool, **kwargs):
        """
        :param is_self: True if the event is about the current user.
        """
        super().__init__(*args, is_self=is_self, **kwargs)


class XmppConversationMemberEvent(XmppConversationEvent, XmppUserEvent, ABC):
    """
    Base class for XMPP events about conversation members.
    """

    def __init__(self, *args, is_self: bool, **kwargs):
        """
        :param is_self: True if the event is about the current user.
        """
        super().__init__(*args, is_self=is_self, **kwargs)


class XmppNickChangedEvent(XmppUserEvent, ABC):
    """
    Base class for XMPP nick changed events.
    """

    def __init__(
        self, *args, old_nick: Optional[str], new_nick: Optional[str], **kwargs
    ):
        """
        :param old_nick: Old nick.
        :param new_nick: New nick.
        """
        super().__init__(*args, old_nick=old_nick, new_nick=new_nick, **kwargs)


class XmppConnectedEvent(XmppEvent):
    """
    Event triggered when the registered XMPP client connects to the server.
    """


class XmppDisconnectedEvent(XmppEvent):
    """
    Event triggered when the registered XMPP client disconnects from the server.
    """

    def __init__(self, *args, reason: Optional[Union[str, Exception]] = None, **kwargs):
        """
        :param reason: The reason of the disconnection.
        """
        super().__init__(*args, reason=str(reason) if reason else None, **kwargs)


class XmppUserAvailableEvent(XmppUserEvent):
    """
    Event triggered when a user the client is subscribed to becomes available.
    """


class XmppUserUnavailableEvent(XmppUserEvent):
    """
    Event triggered when a user the client is subscribed to becomes unavailable.
    """


class XmppRoomUserAvailableEvent(XmppRoomOccupantEvent):
    """
    Event triggered when a user in a joined room becomes available.
    """


class XmppRoomUserUnavailableEvent(XmppRoomOccupantEvent):
    """
    Event triggered when a user in a joined room becomes unavailable.
    """


class XmppMessageReceivedEvent(XmppUserEvent):
    """
    Event triggered when the registered XMPP client receives a message.
    """

    def __init__(self, *args, body: str, **kwargs):
        """
        :param body: The body of the message.
        """
        super().__init__(*args, body=body, **kwargs)


class XmppRoomMessageReceivedEvent(XmppMessageReceivedEvent, XmppRoomOccupantEvent):
    """
    Event triggered when a message is received on a multi-user conversation
    joined by the client.
    """


class XmppRoomInviteAcceptedEvent(XmppRoomEvent):
    """
    Event triggered when an invite to a room is accepted.
    """


class XmppRoomInviteRejectedEvent(XmppRoomEvent):
    """
    Event triggered when an invite to a room is rejected.
    """


class XmppRoomJoinEvent(XmppRoomOccupantEvent):
    """
    Event triggered when a user joins a room.
    """

    def __init__(self, *args, members: Optional[Iterable[str]] = None, **kwargs):
        """
        :param members: List of IDs of the joined members.
        """
        super().__init__(*args, members=list(set(members or [])), **kwargs)


class XmppRoomLeaveEvent(XmppRoomOccupantEvent):
    """
    Event triggered when a user leaves a room.
    """


class XmppRoomEnterEvent(XmppRoomOccupantEvent):
    """
    Event triggered when a user first enters a room.
    """


class XmppRoomExitEvent(XmppRoomOccupantEvent):
    """
    Event triggered when a user exits a room.
    """

    def __init__(self, *args, reason: Optional[str] = None, **kwargs):
        """
        :param reason: Exit reason.
        """
        super().__init__(*args, reason=reason, **kwargs)


class XmppRoomTopicChangedEvent(XmppRoomEvent):
    """
    Event triggered when the topic of a room is changed.
    """

    def __init__(
        self,
        *args,
        topic: Optional[str] = None,
        changed_by: Optional[str] = None,
        **kwargs
    ):
        """
        :param topic: New room topic.
        :param changed_by: Nick of the user who changed the topic.
        """
        super().__init__(*args, topic=topic, changed_by=changed_by, **kwargs)


class XmppPresenceChangedEvent(XmppUserEvent):
    """
    Event triggered when the reported presence of a user in the contacts list
    changes.
    """

    def __init__(self, *args, status: Optional[str], **kwargs):
        """
        :param status: New presence status.
        """
        super().__init__(*args, status=status, **kwargs)


class XmppRoomPresenceChangedEvent(XmppPresenceChangedEvent, XmppRoomEvent):
    """
    Event triggered when the reported presence of a user in a room changes.
    """


class XmppRoomAffiliationChangedEvent(XmppRoomOccupantEvent):
    """
    Event triggered when the affiliation of a user in a room changes.
    """

    def __init__(
        self,
        *args,
        affiliation: str,
        changed_by: Optional[str] = None,
        reason: Optional[str] = None,
        **kwargs
    ):
        """
        :param affiliation: New affiliation.
        :param changed_by: Nick of the user who changed the affiliation.
        :param reason: Affiliation change reason.
        """
        super().__init__(
            *args,
            affiliation=affiliation,
            changed_by=changed_by,
            reason=reason,
            **kwargs
        )


class XmppRoomRoleChangedEvent(XmppRoomOccupantEvent):
    """
    Event triggered when the role of a user in a room changes.
    """

    def __init__(
        self,
        *args,
        role: str,
        changed_by: Optional[str] = None,
        reason: Optional[str] = None,
        **kwargs
    ):
        """
        :param role: New role.
        :param changed_by: Nick of the user who changed the role.
        :param reason: Role change reason.
        """
        super().__init__(
            *args, role=role, changed_by=changed_by, reason=reason, **kwargs
        )


class XmppRoomNickChangedEvent(XmppNickChangedEvent, XmppRoomOccupantEvent):
    """
    Event triggered when a user in a room changes their nick.
    """


class XmppRoomInviteEvent(XmppRoomEvent, XmppUserEvent):
    """
    Event triggered when the client is invited to join a room.
    """

    def __init__(
        self,
        *args,
        mode: str,
        password: Optional[str] = None,
        reason: Optional[str] = None,
        **kwargs
    ):
        """
        :param user_id: The user who sent the invite.
        :param mode: Invite mode, either ``DIRECT`` or ``MEDIATED``.
        :param password: The room password.
        :param reason: Optional invite reason.
        """
        super().__init__(*args, mode=mode, password=password, reason=reason, **kwargs)


class XmppConversationAddedEvent(XmppConversationEvent):
    """
    Event triggered when a conversation is added to the client's list.
    """

    def __init__(self, *args, members: Optional[Iterable[str]] = None, **kwargs):
        """
        :param members: Jabber IDs of the conversation members.
        """
        super().__init__(*args, members=list(set(members or [])), **kwargs)


class XmppConversationEnterEvent(XmppConversationEvent):
    """
    Event triggered when the user enters a conversation.
    """


class XmppConversationExitEvent(XmppConversationEvent):
    """
    Event triggered when the user exits a conversation.
    """


class XmppConversationNickChangedEvent(
    XmppNickChangedEvent, XmppConversationMemberEvent
):
    """
    Event triggered when a user in a p2p conversation changes their nick.
    """


class XmppConversationJoinEvent(XmppConversationMemberEvent):
    """
    Event triggered when a user enters a conversation.
    """


class XmppConversationLeaveEvent(XmppConversationMemberEvent):
    """
    Event triggered when the user leaves a conversation.
    """


class XmppContactAddRequestEvent(XmppUserEvent):
    """
    Event triggered when a user adds the client Jabber ID to their contacts
    list.
    """


class XmppContactAddRequestAcceptedEvent(XmppUserEvent):
    """
    Event triggered when a user contact add request is accepted.
    """


class XmppContactAddRequestRejectedEvent(XmppUserEvent):
    """
    Event triggered when a user contact add request is rejected.
    """
