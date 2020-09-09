from typing import Optional

from platypush.message.event import Event
from platypush.plugins.mail import Mail


class MailEvent(Event):
    def __init__(self, mailbox: str, message: Optional[Mail] = None, *args, **kwargs):
        super().__init__(*args, mailbox=mailbox, message=message or {}, **kwargs)


class MailReceivedEvent(MailEvent):
    """
    Triggered when a new email is received.
    """
    pass


class MailSeenEvent(MailEvent):
    """
    Triggered when a previously unseen email is seen.
    """
    pass


class MailFlaggedEvent(MailEvent):
    """
    Triggered when a message is marked as flagged/starred.
    """
    pass


class MailUnflaggedEvent(MailEvent):
    """
    Triggered when a message previously marked as flagged/starred is unflagged.
    """
    pass


# vim:sw=4:ts=4:et:
