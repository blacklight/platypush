import functools
import importlib
import logging

from platypush.config import Config

modules = {}

def get_or_load_plugin(plugin_name, reload=False):
    global modules

    if plugin_name in modules and not reload:
        return modules[plugin_name]

    try:
        module = importlib.import_module('platypush.plugins.' + plugin_name)
    except ModuleNotFoundError as e:
        logging.warn('No such plugin: {}'.format(plugin_name))
        raise RuntimeError(e)

    # e.g. plugins.music.mpd main class: MusicMpdPlugin
    cls_name = functools.reduce(
        lambda a,b: a.title() + b.title(),
        (plugin_name.title().split('.'))
    ) + 'Plugin'

    plugin_conf = Config.get_plugins()[plugin_name] \
        if plugin_name in Config.get_plugins() else {}

    try:
        plugin = getattr(module, cls_name)(**plugin_conf)
        modules[plugin_name] = plugin
    except AttributeError as e:
        logging.warn('No such class in {}: {}'.format(
            plugin_name, cls_name))
        raise RuntimeError(e)

    return plugin


def init_backends(bus=None):
    backends = {}

    for k in Config.get_backends().keys():
        module = importlib.import_module('platypush.backend.' + k)
        cfg = Config.get_backends()[k]

        # e.g. backend.pushbullet main class: PushbulletBackend
        cls_name = functools.reduce(
            lambda a,b: a.title() + b.title(),
            (module.__name__.title().split('.')[2:])
        ) + 'Backend'

        try:
            b = getattr(module, cls_name)(bus=bus, **cfg)
            backends[k] = b
        except AttributeError as e:
            logging.warn('No such class in {}: {}'.format(
                module.__name__, cls_name))
            raise RuntimeError(e)

    return backends


# vim:sw=4:ts=4:et:

