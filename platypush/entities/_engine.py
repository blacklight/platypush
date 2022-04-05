from logging import getLogger
from queue import Queue, Empty
from threading import Thread, Event
from time import time
from typing import Iterable, List

from sqlalchemy import and_, or_, inspect as schema_inspect
from sqlalchemy.orm import Session

from ._base import Entity


class EntitiesEngine(Thread):
    # Processing queue timeout in seconds
    _queue_timeout = 5.0

    def __init__(self):
        obj_name = self.__class__.__name__
        super().__init__(name=obj_name)
        self.logger = getLogger(name=obj_name)
        self._queue = Queue()
        self._should_stop = Event()

    def post(self, *entities: Entity):
        for entity in entities:
            self._queue.put(entity)

    @property
    def should_stop(self) -> bool:
        return self._should_stop.is_set()

    def stop(self):
        self._should_stop.set()

    def run(self):
        super().run()
        self.logger.info('Started entities engine')

        while not self.should_stop:
            msgs = []
            last_poll_time = time()

            while not self.should_stop and (
                time() - last_poll_time < self._queue_timeout
            ):
                try:
                    msg = self._queue.get(block=True, timeout=0.5)
                except Empty:
                    continue

                if msg:
                    msgs.append(msg)

            if not msgs or self.should_stop:
                continue

            self._process_entities(*msgs)

        self.logger.info('Stopped entities engine')

    def _get_if_exist(
        self, session: Session, entities: Iterable[Entity]
    ) -> Iterable[Entity]:
        existing_entities = {
            (entity.external_id or entity.name, entity.plugin): entity
            for entity in session.query(Entity)
            .filter(
                or_(
                    *[
                        and_(
                            Entity.external_id == entity.external_id,
                            Entity.plugin == entity.plugin,
                        )
                        if entity.external_id is not None
                        else and_(
                            Entity.name == entity.name, Entity.plugin == entity.plugin
                        )
                        for entity in entities
                    ]
                )
            )
            .all()
        }

        return [
            existing_entities.get(
                (entity.external_id or entity.name, entity.plugin), None
            )
            for entity in entities
        ]

    def _merge_entities(
        self, entities: List[Entity], existing_entities: List[Entity]
    ) -> List[Entity]:
        def merge(entity: Entity, existing_entity: Entity) -> Entity:
            inspector = schema_inspect(entity.__class__)
            columns = [col.key for col in inspector.mapper.column_attrs]
            for col in columns:
                if col not in ('id', 'created_at'):
                    setattr(existing_entity, col, getattr(entity, col))

            return existing_entity

        new_entities = []
        entities_map = {}

        # Get the latest update for each ((id|name), plugin) record
        for e in entities:
            key = ((e.external_id or e.name), e.plugin)
            entities_map[key] = e

        # Retrieve existing records and merge them
        for i, entity in enumerate(entities):
            existing_entity = existing_entities[i]
            if existing_entity:
                entity = merge(entity, existing_entity)

            new_entities.append(entity)

        return new_entities

    def _process_entities(self, *entities: Entity):
        from platypush.context import get_plugin

        with get_plugin('db').get_session() as session:  # type: ignore
            existing_entities = self._get_if_exist(session, entities)
            entities = self._merge_entities(entities, existing_entities)  # type: ignore
            session.add_all(entities)
            session.commit()
