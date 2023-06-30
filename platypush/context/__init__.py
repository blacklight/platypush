import asyncio
import importlib
import logging

from dataclasses import dataclass, field
from threading import RLock
from typing import Optional, Any

from ..bus import Bus
from ..config import Config
from ..utils import get_enabled_plugins, get_plugin_name_by_class

logger = logging.getLogger('platypush:context')


@dataclass
class Context:
    """
    Data class to hold the context of the application.
    """

    # backend_name -> backend_instance
    backends: dict = field(default_factory=dict)
    # plugin_name -> plugin_instance
    plugins: dict = field(default_factory=dict)
    # Reference to the main application bus
    bus: Optional[Bus] = None


_ctx = Context()

# # Map: backend_name -> backend_instance
# backends = {}

# # Map: plugin_name -> plugin_instance
# plugins = {}

# Map: plugin_name -> init_lock to make sure that a plugin isn't initialized
# multiple times
plugins_init_locks = {}

# Reference to the main application bus
# main_bus = None


def get_context() -> Context:
    """
    Get the current application context.
    """

    return _ctx


def register_backends(bus=None, global_scope=False, **kwargs):
    """
    Initialize the backend objects based on the configuration and returns a
        name -> backend_instance map.

    Params:
        bus -- If specific (it usually should), the messages processed by the
            backends will be posted on this bus.
        kwargs -- Any additional key-value parameters required to initialize
            the backends
    """

    if bus:
        _ctx.bus = bus

    if global_scope:
        backends = _ctx.backends
    else:
        backends = {}

    for name, cfg in Config.get_backends().items():
        module = importlib.import_module('platypush.backend.' + name)

        # e.g. backend.pushbullet main class: PushbulletBackend
        cls_name = ''
        for token in module.__name__.title().split('.')[2:]:
            cls_name += token.title()
        cls_name += 'Backend'

        try:
            b = getattr(module, cls_name)(bus=bus, **cfg, **kwargs)
            backends[name] = b
        except AttributeError as e:
            logger.warning('No such class in %s: %s', module.__name__, cls_name)
            raise RuntimeError(e) from e

    return backends


def register_plugins(bus=None):
    """
    Register and start all the ``RunnablePlugin`` configured implementations.
    """
    from ..plugins import RunnablePlugin

    for plugin in get_enabled_plugins().values():
        if isinstance(plugin, RunnablePlugin):
            plugin.bus = bus
            plugin.start()


def get_backend(name):
    """Returns the backend instance identified by name if it exists"""

    return _ctx.backends.get(name)


# pylint: disable=too-many-branches
def get_plugin(plugin, plugin_name=None, reload=False):
    """
    Registers a plugin instance by name if not registered already, or returns
    the registered plugin instance.

    :param plugin: Plugin name or class type.
    :param plugin_name: Plugin name, kept only for backwards compatibility.
    :param reload: If ``True``, the plugin will be reloaded if it's already
        been registered.
    """
    from ..plugins import Plugin, RunnablePlugin

    if isinstance(plugin, str):
        name = plugin
    elif plugin_name:
        name = plugin_name
    elif issubclass(plugin, Plugin):
        name = get_plugin_name_by_class(plugin)  # type: ignore
    else:
        raise TypeError(f'Invalid plugin type/name: {plugin}')

    assert name, 'No plugin name provided'
    if name not in plugins_init_locks:
        plugins_init_locks[name] = RLock()

    if name in _ctx.plugins and not reload:
        return _ctx.plugins[name]

    module_name = None
    if isinstance(plugin, str):
        module_name = f'platypush.plugins.{name}'
    elif issubclass(plugin, Plugin):
        module_name = plugin.__module__
    else:
        raise RuntimeError(f'Invalid plugin type/name: {plugin}')

    try:
        plugin = importlib.import_module(module_name)
    except ImportError as e:
        logger.warning('No such plugin: %s', name)
        raise RuntimeError(e) from e

    # e.g. plugins.music.mpd main class: MusicMpdPlugin
    cls_name = ''
    for token in name.split('.'):
        if token:
            cls_name += token[0].upper() + token[1:]
    cls_name += 'Plugin'

    plugin_conf = Config.get_plugins()[name] if name in Config.get_plugins() else {}

    if 'disabled' in plugin_conf:
        if plugin_conf['disabled'] is True:
            return None
        del plugin_conf['disabled']

    if 'enabled' in plugin_conf:
        if plugin_conf['enabled'] is False:
            return None
        del plugin_conf['enabled']

    try:
        plugin_class = getattr(plugin, cls_name)
    except AttributeError as e:
        logger.warning('No such class in %s: %s [error: %s]', name, cls_name, e)
        raise RuntimeError(e) from e

    with plugins_init_locks[name]:
        plugin = _ctx.plugins.get(name)
        if plugin:
            if not reload:
                return _ctx.plugins[name]
            if isinstance(plugin, RunnablePlugin):
                plugin.stop()

        _ctx.plugins[name] = plugin_class(**plugin_conf)

    return _ctx.plugins[name]


def get_bus() -> Bus:
    """
    Get or register the main application bus.
    """
    from platypush.bus.redis import RedisBus

    if _ctx.bus:
        return _ctx.bus

    _ctx.bus = RedisBus()
    return _ctx.bus


def get_or_create_event_loop() -> asyncio.AbstractEventLoop:
    """
    Get or create a new event loop
    """
    try:
        loop = asyncio.get_event_loop()
    except (DeprecationWarning, RuntimeError):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop


class Variable:
    """
    Utility class to wrap platform variables in your custom scripts.
    Usage:

        .. code-block:: python

            # Pass `persisted=False` to get/set an in-memory variable
            # on the Redis instance (default: the variable is
            # persisted on the internal database)
            var = Variable('myvar')
            value = var.get()
            var.set('new value')

    """

    def __init__(self, name: str, persisted: bool = True):
        self.name = name
        self._persisted = persisted

    def get(self) -> Optional[Any]:
        plugin = get_plugin('variable')
        getter = getattr(plugin, 'get' if self._persisted else 'mget')
        return getter(self.name).output.get(self.name)

    def set(self, value: Any):
        plugin = get_plugin('variable')
        setter = getattr(plugin, 'set' if self._persisted else 'mset')
        setter(**{self.name: value})


# vim:sw=4:ts=4:et:
