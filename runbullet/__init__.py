#!/usr/bin/env python

import functools
import importlib
import os
import logging
import json
import socket
import subprocess
import sys
import time
import websocket
import yaml

from threading import Thread
from getopt import getopt

__author__ = 'Fabio Manganiello <info@fabiomanganiello.com>'

#-----------#

config = {}
modules = {}
wrkdir = os.path.dirname(os.path.realpath(__file__))


def on_open(ws):
    logging.info('Connection opened')


def on_close(ws):
    logging.info('Connection closed')


def on_error(ws, error):
    logging.error(error)


def _init_plugin(plugin_name, reload=False):
    global modules
    global config

    if plugin_name in modules and not reload:
        return modules[plugin_name]

    try:
        logging.warn(__package__ + '.plugins.' + plugin_name)
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


def _exec_func(body, retry=True):
    args = {}
    plugin_name = body['plugin']

    if 'args' in body:
        args = json.loads(body['args']) \
            if isinstance(body['args'], str) \
            else body['args']

    try:
        plugin = _init_plugin(plugin_name)
    except RuntimeError as e:  # Module/class not found
        return

    try:
        ret = plugin.run(args)
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
            logging.info('Reloading plugin {} and retrying'.format(plugin_name))
            _init_plugin(plugin_name, reload=True)
            _exec_func(body, retry=False)


def _on_push(ws, data):
    global config

    data = json.loads(data)
    if data['type'] == 'tickle' and data['subtype'] == 'push':
        logging.debug('Received push tickle')
        return

    if data['type'] != 'push':
        return  # Not a push notification

    push = data['push']
    logging.debug('Received push: {}'.format(push))

    if 'body' not in push:
        return

    body = push['body']
    try:
        body = json.loads(body)
    except ValueError as e:
        return

    if 'target' not in body or body['target'] != config['device_id']:
        return  # Not for me

    logging.info('Received push addressed to me: {}'.format(body))

    if 'plugin' not in body:
        logging.warn('No plugin specified')
        return

    thread = Thread(target=_exec_func, args=(body,))
    thread.start()

def on_push(ws, data):
    try:
        _on_push(ws, data)
    except Exception as e:
        on_error(ws, e)


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

    if 'device_id' not in config:
        config['device_id'] = socket.gethostname()

    if 'debug' in config:
        DEBUG = config['debug']

    if DEBUG:
        logging.basicConfig(level=logging.DEBUG)
        websocket.enableTrace(True)
    else:
        logging.basicConfig(level=logging.INFO)

    ws = websocket.WebSocketApp('wss://stream.pushbullet.com/websocket/' +
                                config['pushbullet']['token'],
                                on_message = on_push,
                                on_error = on_error,
                                on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()


if __name__ == '__main__':
    main()

