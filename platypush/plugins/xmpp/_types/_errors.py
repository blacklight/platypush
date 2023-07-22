from dataclasses import dataclass
from typing import Final


@dataclass
class Errors:
    """
    A static class to model plugin error messages.
    """

    CLIENT: Final[str] = 'The XMPP client is not connected'
    HANDLERS: Final[str] = 'No registered XMPP handlers found'
    LOOP: Final[str] = 'The event loop is not running'
    NO_INVITE: Final[str] = 'No such conversation invite'
    NO_USER: Final[str] = 'No such user'
    ROOM_NOT_JOINED: Final[str] = 'The bot has not joined this room'
    USER_ID_OR_ROOM_ID: Final[str] = 'You should specify either user_id or room_id'
