import asyncio
import importlib
import logging

from threading import RLock

from ..config import Config

logger = logging.getLogger('platypush:context')

# Map: backend_name -> backend_instance
backends = {}

# Map: plugin_name -> plugin_instance
plugins = {}

# Map: plugin_name -> init_lock to make sure that a plugin isn't initialized
# multiple times
plugins_init_locks = {}

# Reference to the main application bus
main_bus = None

def register_backends(bus=None, global_scope=False, **kwargs):
    """ Initialize the backend objects based on the configuration and returns
        a name -> backend_instance map.
    Params:
        bus -- If specific (it usually should), the messages processed by the
            backends will be posted on this bus.

        kwargs -- Any additional key-value parameters required to initialize the backends
        """

    global main_bus
    if bus:
        main_bus = bus

    if global_scope:
        global backends
    else:
        backends = {}

    for (name, cfg) in Config.get_backends().items():
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
            logger.warning('No such class in {}: {}'.format(
                module.__name__, cls_name))
            raise RuntimeError(e)

    return backends

def get_backend(name):
    """ Returns the backend instance identified by name if it exists """

    global backends
    return backends.get(name)


def get_plugin(plugin_name, reload=False):
    """ Registers a plugin instance by name if not registered already, or
        returns the registered plugin instance"""
    global plugins
    global plugins_init_locks

    if plugin_name not in plugins_init_locks:
        plugins_init_locks[plugin_name] = RLock()

    if plugin_name in plugins and not reload:
        return plugins[plugin_name]

    try:
        plugin = importlib.import_module('platypush.plugins.' + plugin_name)
    except ImportError as e:
        logger.warning('No such plugin: {}'.format(plugin_name))
        raise RuntimeError(e)

    # e.g. plugins.music.mpd main class: MusicMpdPlugin
    cls_name = ''
    for token in plugin_name.split('.'):
        cls_name += token.title()
    cls_name += 'Plugin'

    plugin_conf = Config.get_plugins()[plugin_name] \
        if plugin_name in Config.get_plugins() else {}

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
        logger.warning('No such class in {}: {} [error: {}]'.format(plugin_name, cls_name, str(e)))
        raise RuntimeError(e)

    with plugins_init_locks[plugin_name]:
        if plugins.get(plugin_name) and not reload:
            return plugins[plugin_name]
        plugins[plugin_name] = plugin_class(**plugin_conf)

    return plugins[plugin_name]


def get_bus():
    global main_bus
    return main_bus


def get_or_create_event_loop():
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop


# vim:sw=4:ts=4:et:
