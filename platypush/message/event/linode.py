from typing import Optional

from platypush.message.event import Event


class LinodeEvent(Event):
    pass


class LinodeInstanceStatusChanged(LinodeEvent):
    """
    Event triggered when the status of a Linode instance changes.
    """
    def __init__(self, instance: str, status: str, old_status: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, instance=instance, status=status, old_status=old_status, **kwargs)


# vim:sw=4:ts=4:et:
