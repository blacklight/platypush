import json
from logging import getLogger
from queue import Queue, Empty
from threading import Thread, Event, RLock
from time import time
from typing import Iterable, List, Optional

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, make_transient

from platypush.context import get_bus
from platypush.message.event.entities import EntityUpdateEvent

from ._base import Entity, db_url


class EntitiesEngine(Thread):
    # Processing queue timeout in seconds
    _queue_timeout = 2.0

    def __init__(self):
        obj_name = self.__class__.__name__
        super().__init__(name=obj_name)
        self.logger = getLogger(name=obj_name)
        self._queue = Queue()
        self._should_stop = Event()
        self._entities_awaiting_flush = set()
        self._entities_cache_lock = RLock()
        self._entities_cache = {
            'by_id': {},
            'by_external_id_and_plugin': {},
            'by_name_and_plugin': {},
        }

    def _get_db(self):
        from platypush.context import get_plugin

        db = get_plugin('db')
        assert db
        return db

    def _get_cached_entity(self, entity: Entity) -> Optional[dict]:
        if entity.id:
            e = self._entities_cache['by_id'].get(entity.id)
            if e:
                return e

        if entity.external_id and entity.plugin:
            e = self._entities_cache['by_external_id_and_plugin'].get(
                (entity.external_id, entity.plugin)
            )
            if e:
                return e

        if entity.name and entity.plugin:
            e = self._entities_cache['by_name_and_plugin'].get(
                (entity.name, entity.plugin)
            )
            if e:
                return e

    @staticmethod
    def _cache_repr(entity: Entity) -> dict:
        repr_ = entity.to_json()
        repr_.pop('data', None)
        repr_.pop('meta', None)
        repr_.pop('created_at', None)
        repr_.pop('updated_at', None)
        return repr_

    def _cache_entities(self, *entities: Entity, overwrite_cache=False):
        for entity in entities:
            e = self._cache_repr(entity)
            if not overwrite_cache:
                existing_entity = self._entities_cache['by_id'].get(entity.id)
                if existing_entity:
                    for k, v in existing_entity.items():
                        if e.get(k) is None:
                            e[k] = v

            if entity.id:
                self._entities_cache['by_id'][entity.id] = e
            if entity.external_id and entity.plugin:
                self._entities_cache['by_external_id_and_plugin'][
                    (entity.external_id, entity.plugin)
                ] = e
            if entity.name and entity.plugin:
                self._entities_cache['by_name_and_plugin'][
                    (entity.name, entity.plugin)
                ] = e

    def _populate_entity_id_from_cache(self, new_entity: Entity):
        with self._entities_cache_lock:
            cached_entity = self._get_cached_entity(new_entity)
            if cached_entity and cached_entity.get('id'):
                new_entity.id = cached_entity['id']
            if new_entity.id:
                self._cache_entities(new_entity)

    def _init_entities_cache(self):
        with self._get_db().get_session(engine=db_url) as session:
            entities = session.query(Entity).all()
            for entity in entities:
                make_transient(entity)

        with self._entities_cache_lock:
            self._cache_entities(*entities, overwrite_cache=True)

        self.logger.info('Entities cache initialized')

    def _process_event(self, entity: Entity):
        self._populate_entity_id_from_cache(entity)
        if entity.id:
            get_bus().post(EntityUpdateEvent(entity=entity))
        else:
            self._entities_awaiting_flush.add(self._to_entity_awaiting_flush(entity))

    @staticmethod
    def _to_entity_awaiting_flush(entity: Entity):
        e = entity.to_json()
        return json.dumps(
            {k: v for k, v in e.items() if k in {'external_id', 'name', 'plugin'}},
            sort_keys=True,
        )

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
        self._init_entities_cache()

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
                    # Trigger an EntityUpdateEvent if there has
                    # been a change on the entity state
                    self._process_event(msg)

            if not msgs or self.should_stop:
                continue

            try:
                self._process_entities(*msgs)
            except Exception as e:
                self.logger.error('Error while processing entity updates: ' + str(e))
                self.logger.exception(e)

        self.logger.info('Stopped entities engine')

    def _get_if_exist(
        self, session: Session, entities: Iterable[Entity]
    ) -> Iterable[Entity]:
        existing_entities = {
            (
                str(entity.external_id)
                if entity.external_id is not None
                else entity.name,
                entity.plugin,
            ): entity
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
                            Entity.name == entity.name,
                            Entity.type == entity.type,
                            Entity.plugin == entity.plugin,
                        )
                        for entity in entities
                    ]
                )
            )
            .all()
        }

        return [
            existing_entities.get(
                (
                    str(entity.external_id)
                    if entity.external_id is not None
                    else entity.name,
                    entity.plugin,
                ),
                None,
            )
            for entity in entities
        ]

    def _merge_entities(
        self, entities: List[Entity], existing_entities: List[Entity]
    ) -> List[Entity]:
        def merge(entity: Entity, existing_entity: Entity) -> Entity:
            columns = [col.key for col in entity.columns]
            for col in columns:
                if col == 'meta':
                    existing_entity.meta = {  # type: ignore
                        **(existing_entity.meta or {}),  # type: ignore
                        **(entity.meta or {}),  # type: ignore
                    }
                elif col not in ('id', 'created_at'):
                    setattr(existing_entity, col, getattr(entity, col))

            return existing_entity

        def entity_key(entity: Entity):
            return ((entity.external_id or entity.name), entity.plugin)

        new_entities = {}
        entities_map = {}

        # Get the latest update for each ((id|name), plugin) record
        for e in entities:
            entities_map[entity_key(e)] = e

        # Retrieve existing records and merge them
        for i, entity in enumerate(entities):
            existing_entity = existing_entities[i]
            if existing_entity:
                entity = merge(entity, existing_entity)

            new_entities[entity_key(entity)] = entity

        return list(new_entities.values())

    def _process_entities(self, *entities: Entity):
        with self._get_db().get_session(engine=db_url) as session:
            # Ensure that the internal IDs are set to null before the merge
            for e in entities:
                e.id = None  # type: ignore

            existing_entities = self._get_if_exist(session, entities)
            entities = self._merge_entities(entities, existing_entities)  # type: ignore
            session.add_all(entities)
            session.commit()

            for e in entities:
                session.expunge(e)

        with self._entities_cache_lock:
            for entity in entities:
                self._cache_entities(entity, overwrite_cache=True)

        entities_awaiting_flush = {*self._entities_awaiting_flush}
        for entity in entities:
            e = self._to_entity_awaiting_flush(entity)
            if e in entities_awaiting_flush:
                self._process_event(entity)
                self._entities_awaiting_flush.remove(e)
