import functools
import importlib
import os
import logging
import json
import socket
import sys
import websocket
import yaml

from queue import Queue
from threading import Thread
from getopt import getopt

__author__ = 'Fabio Manganiello <info@fabiomanganiello.com>'

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


def _exec_func(args, retry=True):
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
        ret = plugin.run(method=method_name, **args)
        out = None
        err = None

        if isinstance(ret, list):
            out = ret[0]
            err = ret[1] if len(ret) > 1 else None
        elif ret is not None:
            out = ret

        if out:
            logging.info('Command output: {}'.format(out))

        if err:
            logging.warn('Command error: {}'.format(err))
    except Exception as e:
        logging.exception(e)
        if retry:
            # Put the action back where it was before retrying
            args['action'] = action

            logging.info('Reloading plugin {} and retrying'.format(module_name))
            _init_plugin(module_name, reload=True)
            _exec_func(args, retry=False)


def on_msg(msg):
    Thread(target=_exec_func, args=(msg,)).start()


def parse_config_file(config_file=None):
    global config

    if config_file:
        locations = [config_file]
    else:
        locations = [
            # ./config.yaml
            os.path.join(wrkdir, 'config.yaml'),
            # ~/.config/runbullet/config.yaml
            os.path.join(os.environ['HOME'], '.config', 'runbullet', 'config.yaml'),
            # /etc/runbullet/config.yaml
            os.path.join(os.sep, 'etc', 'runbullet', 'config.yaml'),
        ]

    for loc in locations:
        try:
            with open(loc,'r') as f:
                config = yaml.load(f)
        except FileNotFoundError as e:
            pass

    return config


def get_backends(config):
    backends = []

    for k in config.keys():
        if k.startswith('backend.') and (
                'disabled' not in config[k] or not config[k]['disabled']):
            module = importlib.import_module(__package__ + '.' + k)

            # e.g. backend.pushbullet main class: PushbulletBackend
            cls_name = functools.reduce(
                lambda a,b: a.title() + b.title(),
                (module.__name__.title().split('.')[2:])
            ) + 'Backend'

            try:
                b = getattr(module, cls_name)(config[k])
                backends.append(b)
            except AttributeError as e:
                logging.warn('No such class in {}: {}'.format(
                    module.__name__, cls_name))
                raise RuntimeError(e)

    return backends

def get_device_id():
    global config
    return config['device_id']


def main():
    DEBUG = False
    config_file = None

    plugins_dir = os.path.join(wrkdir, 'plugins')
    sys.path.insert(0, plugins_dir)

    optlist, args = getopt(sys.argv[1:], 'vh')
    for opt, arg in optlist:
        if opt == '-c':
            config_file = arg
        if opt == '-v':
            DEBUG = True
        elif opt == '-h':
            print('''
Usage: {} [-v] [-h] [-c <config_file>]
    -v  Enable debug mode
    -h  Show this help
    -c  Path to the configuration file (default: ./config.yaml)
'''.format(sys.argv[0]))
            return

    config = parse_config_file(config_file)
    logging.info('Configuration dump: {}'.format(config))

    if 'device_id' not in config:
        config['device_id'] = socket.gethostname()

    if 'debug' in config:
        DEBUG = config['debug']

    if DEBUG:
        logging.basicConfig(level=logging.DEBUG)
        websocket.enableTrace(True)
    else:
        logging.basicConfig(level=logging.INFO)

    mq = Queue()
    backends = get_backends(config)

    for backend in backends:
        backend.mq = mq
        backend.start()

    while True:
        try:
            on_msg(mq.get())
        except KeyboardInterrupt:
            return

if __name__ == '__main__':
    main()

# vim:sw=4:ts=4:et:

