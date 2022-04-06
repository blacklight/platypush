from typing import Union

from platypush.entities import Entity
from platypush.message.event import Event


class EntityUpdateEvent(Event):
    """
    This even is triggered whenever an entity of any type (a switch, a light,
    a sensor, a media player etc.) updates its state.
    """

    def __init__(self, entity: Union[Entity, dict], *args, **kwargs):
        if isinstance(entity, Entity):
            entity = entity.to_json()
        super().__init__(entity=entity, *args, **kwargs)


# vim:sw=4:ts=4:et:
