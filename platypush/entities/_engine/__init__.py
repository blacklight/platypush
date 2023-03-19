from logging import getLogger
from threading import Thread, Event
from typing import Dict, Optional

from platypush.context import get_bus
from platypush.entities import Entity
from platypush.message.event.entities import EntityUpdateEvent
from platypush.utils import set_thread_name

from platypush.entities._base import EntityKey, EntitySavedCallback
from platypush.entities._engine.queue import EntitiesQueue
from platypush.entities._engine.repo import EntitiesRepository


class EntitiesEngine(Thread):
    """
    This thread runs the "brain" of the entities data persistence logic.

    Its purpose is to:

        1. Consume entities from a queue (synchronized with the upstream
           integrations that produce/handle them). The producer/consumer model
           ensure that only this thread writes to the database, packs events
           together (preventing excessive writes and throttling events), and
           prevents race conditions when SQLite is used.
        2. Merge any existing entities with their newer representations.
        3. Update the entities taxonomy.
        4. Persist the new state to the entities database.
        5. Trigger events for the updated entities.

    """

    def __init__(self) -> None:
        obj_name = self.__class__.__name__
        super().__init__(name=obj_name)

        self.logger = getLogger(name=obj_name)
        self._should_stop = Event()
        """ Event used to synchronize stop events downstream."""
        self._running = Event()
        """
        Event used to synchronize other threads to wait for the engine to
        start.
        """
        self._queue = EntitiesQueue(stop_event=self._should_stop)
        """ Queue where all entity upsert requests are received."""
        self._repo = EntitiesRepository()
        """ The repository of the processed entities. """
        self._callbacks: Dict[EntityKey, EntitySavedCallback] = {}
        """ (external_id, plugin) -> callback mapping"""

    def post(self, *entities: Entity, callback: Optional[EntitySavedCallback] = None):
        if callback:
            for entity in entities:
                self._callbacks[entity.entity_key] = callback

        self._queue.put(*entities)

    def wait_start(self, timeout: Optional[float] = None) -> None:
        started = self._running.wait(timeout=timeout)
        if not started:
            raise TimeoutError(
                f'Timeout waiting for {self.__class__.__name__} to start.'
            )

    @property
    def should_stop(self) -> bool:
        return self._should_stop.is_set()

    def stop(self):
        self._should_stop.set()

    def notify(self, *entities: Entity):
        """
        Trigger an EntityUpdateEvent if the entity has been persisted, or queue
        it to the list of entities whose notifications will be flushed when the
        session is committed. It will also invoke any registered callbacks.
        """
        for entity in entities:
            get_bus().post(EntityUpdateEvent(entity=entity))
            self._process_callback(entity)

    def _process_callback(self, entity: Entity) -> None:
        """
        Process the callback for the given entity.
        """
        callback = self._callbacks.pop(entity.entity_key, None)
        if callback:
            try:
                callback(entity)
            except Exception as e:
                self.logger.error(
                    'Error while notifying updates for entity ID %d via %s: %s',
                    entity.id,
                    callback,
                    e,
                )
                self.logger.exception(e)

    def run(self):
        super().run()
        set_thread_name('entities')
        self.logger.info('Started entities engine')
        self._running.set()

        try:
            while not self.should_stop:
                # Get a batch of entity updates forwarded by other integrations
                entities = self._queue.get()
                if not entities or self.should_stop:
                    continue

                # Store the batch of entities
                try:
                    entities = self._repo.save(*entities)
                except Exception as e:
                    self.logger.error('Error while processing entity updates: %s', e)
                    self.logger.exception(e)
                    continue

                # Trigger EntityUpdateEvent events
                self.notify(*entities)
        finally:
            self.logger.info('Stopped entities engine')
            self._running.clear()
