from typing import Optional

from platypush.message.event import Event


class LinodeEvent(Event):
    """
    Base Linode event class.
    """


class LinodeInstanceStatusChanged(LinodeEvent):
    """
    Event triggered when the status of a Linode instance changes.
    """

    def __init__(
        self,
        *args,
        instance_id: int,
        instance_name: str,
        status: str,
        old_status: Optional[str] = None,
        **kwargs
    ):
        """
        :param instance_id: Linode instance ID.
        :param instance: Linode instance name.
        :param status: New status of the instance.
        :param old_status: Old status of the instance.
        """
        super().__init__(
            *args,
            instance_id=instance_id,
            instance_name=instance_name,
            status=status,
            old_status=old_status,
            **kwargs
        )


# vim:sw=4:ts=4:et:
