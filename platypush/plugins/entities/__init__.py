from queue import Queue, Empty
from threading import Thread
from time import time
from typing import Optional, Any, Collection

from platypush.context import get_plugin
from platypush.entities import Entity, get_plugin_entity_registry, get_entities_registry
from platypush.plugins import Plugin, action


class EntitiesPlugin(Plugin):
    """
    This plugin is used to interact with native platform entities (e.g. switches, lights,
    sensors etc.) through a consistent interface, regardless of the integration type.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _get_db(self):
        db = get_plugin('db')
        assert db
        return db

    @action
    def get(
        self,
        types: Optional[Collection[str]] = None,
        plugins: Optional[Collection[str]] = None,
        **filter,
    ):
        """
        Retrieve a list of entities.

        :param types: Entity types, as specified by the (lowercase) class name and table name.
            Default: all entities.
        :param plugins: Filter by plugin IDs (default: all plugins).
        :param filter: Filter entities with these criteria (e.g. `name`, `id`,
            `state`, `type`, `plugin` etc.)
        """
        entity_registry = get_entities_registry()
        selected_types = []
        all_types = {e.__tablename__.lower(): e for e in entity_registry}

        if types:
            selected_types = {t.lower() for t in types}
            entity_types = {t: et for t, et in all_types.items() if t in selected_types}
            invalid_types = selected_types.difference(entity_types.keys())
            assert not invalid_types, (
                f'No such entity types: {invalid_types}. '
                f'Supported types: {list(all_types.keys())}'
            )

            selected_types = entity_types.keys()

        db = self._get_db()
        with db.get_session() as session:
            query = session.query(Entity)
            if selected_types:
                query = query.filter(Entity.type.in_(selected_types))
            if plugins:
                query = query.filter(Entity.plugin.in_(plugins))
            if filter:
                query = query.filter_by(**filter)

            return [e.to_json() for e in query.all()]

    @action
    def scan(
        self,
        types: Optional[Collection[str]] = None,
        plugins: Optional[Collection[str]] = None,
        timeout: Optional[float] = 30.0,
    ):
        """
        (Re-)scan entities and return the updated results.

        :param types: Filter by entity types (e.g. `switch`, `light`, `sensor` etc.).
        :param plugins: Filter by plugin names (e.g. `switch.tplink` or `light.hue`).
        :param timeout: Scan timeout in seconds. Default: 30.
        """
        filter = {}
        plugin_registry = get_plugin_entity_registry()

        if plugins:
            filter['plugins'] = plugins
            plugin_registry['by_plugin'] = {
                plugin: plugin_registry['by_plugin'][plugin]
                for plugin in plugins
                if plugin in plugin_registry['by_plugin']
            }

        if types:
            filter['types'] = types
            filter_entity_types = set(types)
            plugin_registry['by_plugin'] = {
                plugin_name: entity_types
                for plugin_name, entity_types in plugin_registry['by_plugin'].items()
                if any(t for t in entity_types if t in filter_entity_types)
            }

        enabled_plugins = plugin_registry['by_plugin'].keys()

        def worker(plugin_name: str, q: Queue):
            try:
                plugin = get_plugin(plugin_name)
                assert plugin, f'No such configured plugin: {plugin_name}'
                # Force a plugin scan by calling the `status` action
                response = plugin.status()
                assert not response.errors, response.errors
                q.put((plugin_name, response.output))
            except Exception as e:
                q.put((plugin_name, e))

        q = Queue()
        start_time = time()
        results = []
        workers = [
            Thread(target=worker, args=(plugin_name, q))
            for plugin_name in enabled_plugins
        ]

        for w in workers:
            w.start()

        while len(results) < len(workers) and (
            not timeout or (time() - start_time < timeout)
        ):
            try:
                plugin_name, result = q.get(block=True, timeout=0.5)
                if isinstance(result, Exception):
                    self.logger.warning(
                        f'Could not load results from plugin {plugin_name}: {result}'
                    )
                else:
                    results.append(result)
            except Empty:
                continue

        if len(results) < len(workers):
            self.logger.warning('Scan timed out for some plugins')

        for w in workers:
            w.join(timeout=max(0, timeout - (time() - start_time)) if timeout else None)

        return self.get(**filter)

    @action
    def execute(self, id: Any, action: str, *args, **kwargs):
        """
        Execute an action on an entity (for example `on`/`off` on a switch, or `get`
        on a sensor).

        :param id: Entity ID (i.e. the entity's db primary key, not the plugin's external
            or "logical" key)
        :param action: Action that should be run. It should be a method implemented
            by the entity's class.
        :param args: Action's extra positional arguments.
        :param kwargs: Action's extra named arguments.
        """
        db = self._get_db()
        with db.get_session() as session:
            entity = session.query(Entity).filter_by(id=id).one_or_none()

        assert entity, f'No such entity ID: {id}'
        return entity.run(action, *args, **kwargs)


# vim:sw=4:ts=4:et:
