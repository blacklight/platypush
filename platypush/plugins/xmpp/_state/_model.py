from asyncio import Event as AsyncEvent
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Event
from typing import Any, Dict, Iterable, Optional, Set

import aioxmpp
import aioxmpp.im.p2p

from .._types import RoomInvite, UserInvite


@dataclass
class OccupantState:
    """
    Models the state of a room occupant.
    """

    user_id: str
    nick: Optional[str]
    affiliation: Optional[str]
    role: Optional[str]
    is_self: bool
    available: bool
    state: Optional[str]

    @classmethod
    def load(cls, occupant_dict: Dict[str, Any]) -> "OccupantState":
        return cls(
            user_id=occupant_dict["user_id"],
            nick=occupant_dict.get("nick"),
            affiliation=occupant_dict.get("affiliation"),
            role=occupant_dict.get("role"),
            is_self=occupant_dict["is_self"],
            available=occupant_dict["available"],
            state=occupant_dict.get("state"),
        )


@dataclass
class RoomState:
    """
    Models the state of a room.
    """

    room_id: str
    joined: bool
    state: Optional[str]
    nick: Optional[str]
    password: Optional[str]
    members: Dict[str, OccupantState] = field(default_factory=dict)

    @classmethod
    def load(cls, room_dict: Dict[str, Any]) -> "RoomState":
        return cls(
            room_id=room_dict["room_id"],
            joined=room_dict["joined"],
            state=room_dict.get("state"),
            nick=room_dict.get("nick"),
            password=room_dict.get("password"),
            members={
                user_id: OccupantState.load(member)
                for user_id, member in room_dict.get("members", {}).items()
            },
        )


@dataclass
class SerializedState:
    """
    Serialized snapshot of the XMPP state, which can be more easily
    serialized/deserialized to JSON.
    """

    users: Iterable[str] = field(default_factory=list)
    """List of users on the subscriptions/contacts list."""
    rooms: Dict[str, RoomState] = field(default_factory=dict)
    """List of rooms the user has joined."""
    room_invites: Iterable[str] = field(default_factory=list)
    """List of room invites, by room_id."""
    user_invites: Iterable[str] = field(default_factory=list)
    """List of user invites, by user_id."""

    @classmethod
    def load(cls, state: Dict[str, Any]) -> "SerializedState":
        return cls(
            users=state.get("users", []),
            rooms={
                room_id: RoomState.load(room)
                for room_id, room in state.get("rooms", {}).items()
            },
            room_invites=state.get("room_invites", []),
            user_invites=state.get("user_invites", []),
        )


@dataclass
class XmppState:
    """
    Models the state of the XMPP client.
    """

    rooms: Dict[str, aioxmpp.muc.service.Room] = field(default_factory=dict)
    conversations: Dict[str, aioxmpp.im.p2p.Conversation] = field(default_factory=dict)
    users: Set[str] = field(default_factory=set)
    room_invites: Dict[str, RoomInvite] = field(
        default_factory=lambda: defaultdict(RoomInvite)
    )
    user_invites: Dict[str, UserInvite] = field(
        default_factory=lambda: defaultdict(UserInvite)
    )
    disconnect_notified: Event = field(default_factory=Event)
    should_stop: AsyncEvent = field(default_factory=AsyncEvent)
    pending_rooms: Set[str] = field(default_factory=set)
    """Set of rooms that are currently being joined"""

    @staticmethod
    def _occupant_user_id(occupant: aioxmpp.muc.service.Occupant) -> str:
        return (
            str(occupant.direct_jid.replace(resource=None))
            if occupant.direct_jid is not None
            else str(occupant.conversation_jid)
        )

    def asdict(self, return_passwords=True):
        """
        :return: The state of the client as a flat dictionary.
        """
        return {
            "room_invites": list(self.room_invites.keys()),
            "user_invites": list(self.user_invites.keys()),
            "users": list({*self.conversations.keys(), *self.users}),
            "rooms": {
                room_id: {
                    "room_id": str(room.jid),
                    "joined": room.muc_joined,
                    "state": room.muc_state.name,
                    "nick": room.me.nick if room.me else None,
                    **({"password": room.muc_password} if return_passwords else {}),
                    "members": {
                        self._occupant_user_id(member): {
                            "user_id": self._occupant_user_id(member),
                            "nick": member.nick,
                            "affiliation": member.affiliation,
                            "role": member.role,
                            "is_self": member.is_self,
                            "available": member.presence_state.available,
                            "state": (
                                "available"
                                if not member.presence_state.show.value
                                else member.presence_state.show.value
                            ),
                        }
                        for member in room.members
                    },
                }
                for room_id, room in self.rooms.items()
            },
        }

    def serialize(self) -> SerializedState:
        """
        :return: The JSON-friendly dehydrated representation of the state, which
            can be restored across restarts.
        """
        return SerializedState(**self.asdict())
