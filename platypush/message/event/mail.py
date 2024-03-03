from platypush.message.event import Event


class MailEvent(Event):
    """
    Base class for mail events.
    """

    def __init__(self, *args, account: str, folder: str, message, **kwargs):
        super().__init__(
            *args, account=account, folder=folder, message=message, **kwargs
        )


class UnseenMailEvent(MailEvent):
    """
    Triggered when a new email is received or marked as unseen.
    """


class SeenMailEvent(MailEvent):
    """
    Triggered when a previously unseen email is seen.
    """


class FlaggedMailEvent(MailEvent):
    """
    Triggered when a message is marked as flagged/starred.
    """


class UnflaggedMailEvent(MailEvent):
    """
    Triggered when a message previously marked as flagged/starred is unflagged.
    """


# vim:sw=4:ts=4:et:
