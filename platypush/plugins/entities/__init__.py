from queue import Queue, Empty
from threading import Thread
from time import time
from typing import Optional

from platypush.context import get_plugin
from platypush.entities import get_plugin_entity_registry, get_entities_registry
from platypush.plugins import Plugin, action


class EntitiesPlugin(Plugin):
    """
    This plugin is used to interact with native platform entities (e.g. switches, lights,
    sensors etc.) through a consistent interface, regardless of the integration type.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @action
    def get(self, type: str = 'entity', **filter):
        """
        Retrieve a list of entities.

        :param type: Entity type, as specified by the (lowercase) class name and table name.
            Default: `entity` (retrieve all the types)
        :param filter: Filter entities with these criteria (e.g. `name`, `id`,
            `state`, `plugin` etc.)
        """
        entity_registry = get_entities_registry()
        all_types = {e.__tablename__.lower(): e for e in entity_registry}

        entity_type = all_types.get(type.lower())
        assert (
            entity_type
        ), f'No such entity type: {type}. Supported types: {list(all_types.keys())}'

        db = get_plugin('db')
        assert db

        with db.get_session() as session:
            query = session.query(entity_type)
            if filter:
                query = query.filter_by(**filter)

            return [e.to_json() for e in query.all()]

    @action
    def scan(
        self,
        type: Optional[str] = None,
        plugin: Optional[str] = None,
        timeout: Optional[float] = 30.0,
    ):
        """
        (Re-)scan entities and return the updated results.

        :param type: Filter by entity type (e.g. `switch`, `light`, `sensor` etc.). Default: all.
        :param plugin: Filter by plugin name (e.g. `switch.tplink` or `light.hue`). Default: all.
        :param timeout: Scan timeout in seconds. Default: 30.
        """
        filter = {}
        plugin_registry = get_plugin_entity_registry()

        if plugin:
            filter['plugin'] = plugin
            plugin_registry['by_plugin'] = {
                **(
                    {plugin: plugin_registry['by_plugin'][plugin]}
                    if plugin in plugin_registry['by_plugin']
                    else {}
                )
            }

        if type:
            filter['type'] = type
            filter_plugins = set(plugin_registry['by_entity_type'].get(type, []))
            plugin_registry['by_plugin'] = {
                plugin_name: entity_types
                for plugin_name, entity_types in plugin_registry['by_plugin'].items()
                if plugin_name in filter_plugins
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


# vim:sw=4:ts=4:et:
