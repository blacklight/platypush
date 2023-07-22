from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from threading import Event
from typing import Any, Callable, Optional, Type


class InviteTarget(Enum):
    """
    Tells whether the target of an invite is a user or a room.
    """

    USER = 1
    ROOM = 2


@dataclass
class Invite(ABC):
    """
    A class that models the parameters of an invite to a conversation.
    """

    accepted: Optional[bool] = None
    responded: Event = field(default_factory=Event)
    on_accepted: Callable[[], Any] = field(default_factory=lambda: lambda: None)
    on_rejected: Callable[[], Any] = field(default_factory=lambda: lambda: None)

    @property
    @abstractmethod
    def target(self) -> InviteTarget:
        raise NotImplementedError

    def accept(self):
        self.accepted = True
        self.responded.set()
        self.on_accepted()

    def reject(self):
        self.accepted = False
        self.responded.set()
        self.on_rejected()

    def wait_response(self, timeout: Optional[float] = None) -> bool:
        return self.responded.wait(timeout)

    @classmethod
    def by_target(cls, target: InviteTarget) -> Type["Invite"]:
        return {
            InviteTarget.ROOM: RoomInvite,
            InviteTarget.USER: UserInvite,
        }[target]


@dataclass
class RoomInvite(Invite):
    """
    Models an invite to a room.
    """

    @property
    def target(self) -> InviteTarget:
        return InviteTarget.ROOM


@dataclass
class UserInvite(Invite):
    """
    Models an invite to a user's contacts list.
    """

    @property
    def target(self) -> InviteTarget:
        return InviteTarget.USER
