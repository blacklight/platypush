from enum import Enum


class XmppPresence(Enum):
    """
    Models the XMPP presence states.
    """

    AVAILABLE = "available"
    NONE = AVAILABLE
    PLAIN = AVAILABLE
    OFFLINE = "offline"
    XA = "xa"
    EXTENDED_AWAY = XA
    AWAY = "away"
    CHAT = "chat"
    FREE_FOR_CHAT = CHAT
    DND = "dnd"
    DO_NOT_DISTURB = DND
