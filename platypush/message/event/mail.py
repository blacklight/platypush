from typing import Optional, Dict

from platypush.message.event import Event


class MailEvent(Event):
    def __init__(self, mailbox: str, message: Optional[Dict] = None, *args, **kwargs):
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


# vim:sw=4:ts=4:et:
