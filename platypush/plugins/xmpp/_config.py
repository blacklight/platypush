from dataclasses import dataclass
from typing import Optional


@dataclass
class XmppConfig:
    """
    Data class that models the XMPP configuration shared across all submodules.
    """

    auto_accept_invites: bool = True
    """
    Whether or not to automatically accept invites to rooms and buddy lists.
    """

    restore_state: bool = True
    """
    Whether to restore the previous state of the joined rooms and subscriptions
    upon application restart.
    """

    state_file: Optional[str] = None
    """
    The path where the state of the client is persisted across sessions.
    """
