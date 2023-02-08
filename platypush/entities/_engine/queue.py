from queue import Queue, Empty
from threading import Event
from time import time
from typing import List, Optional

from platypush.entities import Entity


class EntitiesQueue(Queue):
    """
    Extends the ``Queue`` class to provide an abstraction that allows to
    getting and putting multiple entities at once and synchronize with the
    upstream caller.
    """

    def __init__(self, stop_event: Optional[Event] = None, timeout: float = 1.0):
        super().__init__()
        self._timeout = timeout
        self._should_stop = stop_event

    @property
    def should_stop(self) -> bool:
        return self._should_stop.is_set() if self._should_stop else False

    def get(self, block=True, timeout=None) -> List[Entity]:
        """
        Returns a batch of entities read from the queue.
        """
        timeout = timeout or self._timeout
        entities = []
        last_poll_time = time()

        while not self.should_stop and (time() - last_poll_time < timeout):
            try:
                entity = super().get(block=block, timeout=0.5)
            except Empty:
                continue

            if entity:
                entities.append(entity)

        return entities

    def put(self, *entities: Entity, block=True, timeout=None):
        """
        This method is called by an entity manager to update and persist the
        state of some entities.
        """
        for entity in entities:
            super().put(entity, block=block, timeout=timeout)
