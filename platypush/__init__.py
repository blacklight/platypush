import functools
import importlib
import os
import logging
import json
import socket
import sys
import traceback
import websocket
import yaml

from queue import Queue
from threading import Thread
from getopt import getopt

from .message.response import Response

__author__ = 'Fabio Manganiello <info@fabiomanganiello.com>'
__version__ = '0.3.2'

#-----------#

config = {}
modules = {}
wrkdir = os.path.dirname(os.path.realpath(__file__))


def _init_plugin(plugin_name, reload=False):
    global modules
    global config

    if plugin_name in modules and not reload:
        return modules[plugin_name]

    try:
        module = importlib.import_module(__package__ + '.plugins.' + plugin_name)
    except ModuleNotFoundError as e:
        logging.warn('No such plugin: {}'.format(plugin_name))
        raise RuntimeError(e)

    # e.g. plugins.music.mpd main class: MusicMpdPlugin
    cls_name = functools.reduce(
        lambda a,b: a.title() + b.title(),
        (plugin_name.title().split('.'))
    ) + 'Plugin'

    plugin_conf = config[plugin_name] if plugin_name in config else {}

    try:
        plugin = getattr(module, cls_name)(plugin_conf)
        modules[plugin_name] = plugin
    except AttributeError as e:
        logging.warn('No such class in {}: {}'.format(
            plugin_name, cls_name))
        raise RuntimeError(e)

    return plugin


def _exec_func(args, backend=None, retry=True):
    origin = args.pop('origin') if 'origin' in args else None
    action = args.pop('action')
    tokens = action.split('.')
    module_name = str.join('.', tokens[:-1])
    method_name = tokens[-1:][0]

    try:
        plugin = _init_plugin(module_name)
    except RuntimeError as e:  # Module/class not found
        logging.exception(e)
        return

    try:
        response = plugin.run(method=method_name, **args)
        if response and response.is_error():
            logging.warn('Response processed with errors: {}'.format(response))
        else:
            logging.info('Processed response: {}'.format(response))
    except Exception as e:
        response = Response(output=None, errors=[e, traceback.format_exc()])
        logging.exception(e)
        if retry:
            # Put the popped args back where they were before retrying
            args['action'] = action; args['origin'] = origin

            logging.info('Reloading plugin {} and retrying'.format(module_name))
            _init_plugin(module_name, reload=True)
            _exec_func(args, backend, retry=False)
    finally:
        if backend: backend.send_response(origin, response)


def on_msg(msg, backend=None):
    Thread(target=_exec_func, args=(msg,backend)).start()


def parse_config_file(config_file=None):
    global config

    if config_file:
        locations = [config_file]
    else:
        locations = [
            # ./config.yaml
            os.path.join(wrkdir, 'config.yaml'),
            # ~/.config/platypush/config.yaml
            os.path.join(os.environ['HOME'], '.config', 'platypush', 'config.yaml'),
            # /etc/platypush/config.yaml
            os.path.join(os.sep, 'etc', 'platypush', 'config.yaml'),
        ]

    for loc in locations:
        try:
            with open(loc,'r') as f:
                config = yaml.load(f)
        except FileNotFoundError as e:
            pass

    for section in config:
        if 'disabled' in config[section] and config[section]['disabled']:
            del config[section]

    if 'logging' not in config:
        config['logging'] = logging.INFO
    else:
        config['logging'] = getattr(logging, config['logging'].upper())

    if 'device_id' not in config:
        config['device_id'] = socket.gethostname()

    return config


def get_backends(config):
    backends = {}

    for k in config.keys():
        if k.startswith('backend.'):
            module = importlib.import_module(__package__ + '.' + k)

            # e.g. backend.pushbullet main class: PushbulletBackend
            cls_name = functools.reduce(
                lambda a,b: a.title() + b.title(),
                (module.__name__.title().split('.')[2:])
            ) + 'Backend'

            # Ignore the pusher attribute here
            if 'pusher' in config[k]: del config[k]['pusher']

            try:
                b = getattr(module, cls_name)(config[k])
                name = '.'.join((k.split('.'))[1:])
                backends[name] = b
            except AttributeError as e:
                logging.warn('No such class in {}: {}'.format(
                    module.__name__, cls_name))
                raise RuntimeError(e)

    return backends


def get_default_pusher_backend(config):
    backends = ['.'.join((k.split('.'))[1:])
                for k in config.keys() if k.startswith('backend.')
                and 'pusher' in config[k] and config[k]['pusher'] is True]

    return backends[0] if backends else None


def get_logging_level():
    global config
    return config['logging']


def get_device_id():
    global config
    return config['device_id'] if 'device_id' in config else None


def main():
    print('Starting platypush v.{}'.format(__version__))

    debug = False
    config_file = None

    plugins_dir = os.path.join(wrkdir, 'plugins')
    sys.path.insert(0, plugins_dir)

    optlist, args = getopt(sys.argv[1:], 'vh')
    for opt, arg in optlist:
        if opt == '-c':
            config_file = arg
        if opt == '-v':
            debug = True
        elif opt == '-h':
            print('''
Usage: {} [-v] [-h] [-c <config_file>]
    -v  Enable debug mode
    -h  Show this help
    -c  Path to the configuration file (default: ./config.yaml)
'''.format(sys.argv[0]))
            return

    config = parse_config_file(config_file)
    if debug: config['logging'] = logging.DEBUG

    logging.basicConfig(level=get_logging_level(), stream=sys.stdout)
    logging.debug('Configuration dump: {}'.format(config))

    mq = Queue()
    backends = get_backends(config)

    for backend in backends.values():
        backend.mq = mq
        backend.start()

    while True:
        try:
            on_msg(mq.get(), backend)
        except KeyboardInterrupt:
            return

if __name__ == '__main__':
    main()

# vim:sw=4:ts=4:et:

