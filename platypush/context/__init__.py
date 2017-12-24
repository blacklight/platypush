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


# vim:sw=4:ts=4:et:

