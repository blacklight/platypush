from logging import getLogger
from threading import Thread, Event

from platypush.entities import Entity
from platypush.utils import set_thread_name

# pylint: disable=no-name-in-module
from platypush.entities._engine.notifier import EntityNotifier

# pylint: disable=no-name-in-module
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

    def __init__(self):
        obj_name = self.__class__.__name__
        super().__init__(name=obj_name)

        self.logger = getLogger(name=obj_name)
        self._should_stop = Event()
        self._queue = EntitiesQueue(stop_event=self._should_stop)
        self._repo = EntitiesRepository()
        self._notifier = EntityNotifier(self._repo._cache)

    def post(self, *entities: Entity):
        self._queue.put(*entities)

    @property
    def should_stop(self) -> bool:
        return self._should_stop.is_set()

    def stop(self):
        self._should_stop.set()

    def run(self):
        super().run()
        set_thread_name('entities')
        self.logger.info('Started entities engine')

        while not self.should_stop:
            # Get a batch of entity updates forwarded by other integrations
            entities = self._queue.get()
            if not entities or self.should_stop:
                continue

            # Trigger/prepare EntityUpdateEvent objects
            for entity in entities:
                self._notifier.notify(entity)

            # Store the batch of entities
            try:
                entities = self._repo.save(*entities)
            except Exception as e:
                self.logger.error('Error while processing entity updates: %s', e)
                self.logger.exception(e)
                continue

            # Flush any pending notifications
            self._notifier.flush(*entities)

        self.logger.info('Stopped entities engine')
