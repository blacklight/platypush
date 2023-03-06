from typing import Union

from platypush.entities import Entity
from platypush.message.event import Event


class EntityEvent(Event):
    def __init__(self, entity: Union[Entity, dict], *args, **kwargs):
        if isinstance(entity, Entity):
            entity = entity.to_dict()
        super().__init__(entity=entity, *args, **kwargs)


class EntityUpdateEvent(EntityEvent):
    """
    This event is triggered whenever an entity of any type (a switch, a light,
    a sensor, a media player etc.) updates its state.
    """


class EntityDeleteEvent(EntityEvent):
    """
    This event is triggered whenever an entity is deleted.
    """


# vim:sw=4:ts=4:et:
