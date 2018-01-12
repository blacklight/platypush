import functools
import importlib
import logging

from ..config import Config

# Map: backend_name -> backend_instance
backends = {}

# Map: plugin_name -> plugin_instance
plugins = {}

def register_backends(bus=None, global_scope=False, **kwargs):
    """ Initialize the backend objects based on the configuration and returns
        a name -> backend_instance map.
    Params:
        bus -- If specific (it usually should), the messages processed by the
            backends will be posted on this bus.

        kwargs -- Any additional key-value parameters required to initialize the backends
        """

    if global_scope:
        global backends
    else:
        backends = {}

    for (name, cfg) in Config.get_backends().items():
        module = importlib.import_module('platypush.backend.' + name)

        # e.g. backend.pushbullet main class: PushbulletBackend
        cls_name = functools.reduce(
            lambda a,b: a.title() + b.title(),
            (module.__name__.title().split('.')[2:])
        ) + 'Backend'

        try:
            b = getattr(module, cls_name)(bus=bus, **cfg, **kwargs)
            backends[name] = b
        except AttributeError as e:
            logging.warning('No such class in {}: {}'.format(
                module.__name__, cls_name))
            raise RuntimeError(e)

    return backends

def get_backend(name):
    """ Returns the backend instance identified by name if it exists """

    global backends
    return backends[name]


def get_plugin(plugin_name, reload=False):
    """ Registers a plugin instance by name if not registered already, or
        returns the registered plugin instance"""
    global plugins

    if plugin_name in plugins and not reload:
        return plugins[plugin_name]

    try:
        plugin = importlib.import_module('platypush.plugins.' + plugin_name)
    except ModuleNotFoundError as e:
        logging.warning('No such plugin: {}'.format(plugin_name))
        raise RuntimeError(e)

    # e.g. plugins.music.mpd main class: MusicMpdPlugin
    cls_name = ''
    for token in plugin_name.split('.'):
        cls_name += token.title()
    cls_name += 'Plugin'

    plugin_conf = Config.get_plugins()[plugin_name] \
        if plugin_name in Config.get_plugins() else {}

    try:
        plugin_class = getattr(plugin, cls_name)
        plugin = plugin_class(**plugin_conf)
        plugins[plugin_name] = plugin
    except AttributeError as e:
        logging.warning('No such class in {}: {}'.format(plugin_name, cls_name))
        raise RuntimeError(e)

    plugins[plugin_name] = plugin
    return plugin

def register_plugin(name, plugin, **kwargs):
    """ Registers a plugin instance by name """
    global plugins

# vim:sw=4:ts=4:et:

