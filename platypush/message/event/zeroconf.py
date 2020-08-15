import enum
from typing import Optional

from platypush.message.event import Event


class ZeroconfEventType(enum.Enum):
    ADD = 'add'
    UPDATE = 'update'
    REMOVE = 'remove'


class ZeroconfEvent(Event):
    def __init__(self, service_event: ZeroconfEventType, service_type: str, service_name: str,
                 service_info: Optional[dict] = None, *args, **kwargs):
        super().__init__(*args, service_event=service_event.value, service_type=service_type,
                         service_name=service_name, service_info=service_info, **kwargs)

        self.service_type = service_type
        self.service_name = service_name
        self.service_info = service_info


class ZeroconfServiceAddedEvent(ZeroconfEvent):
    """
    Event triggered when a service is added or discovered.
    """
    def __init__(self, *args, **kwargs):
        kwargs['service_event'] = ZeroconfEventType.ADD
        super().__init__(*args, **kwargs)


class ZeroconfServiceUpdatedEvent(ZeroconfEvent):
    """
    Event triggered when a service is updated.
    """
    def __init__(self, *args, **kwargs):
        kwargs['service_event'] = ZeroconfEventType.UPDATE
        super().__init__(*args, **kwargs)


class ZeroconfServiceRemovedEvent(ZeroconfEvent):
    """
    Event triggered when a service is removed.
    """
    def __init__(self, *args, **kwargs):
        kwargs['service_event'] = ZeroconfEventType.REMOVE
        super().__init__(*args, **kwargs)


# vim:sw=4:ts=4:et:
