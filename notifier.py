#!/usr/bin/env python

import os
import logging
import json
import socket
import subprocess
import sys
import time
import websocket

from getopt import getopt

__author__ = 'Fabio Manganiello <info@fabiomanganiello.com>'

API_KEY = 'o.EHMMnZneJdpNQv9FSFbyY2busin7floe'
DEVICE_ID = socket.gethostname()
DEBUG = False


def on_open(ws):
    logging.info('Connection opened')


def on_close(ws):
    logging.info('Connection closed')


def on_error(ws, error):
    logging.error(error)


def _on_push(ws, data):
    data = json.loads(data)
    if data['type'] == 'tickle' and data['subtype'] == 'push':
        logging.debug('Received push tickle')
        return

    if data['type'] != 'push':
        return  # Not a push notification

    push = data['push']
    logging.debug('Received push: {}'.format(push))

    body = push['body']
    try:
        body = json.loads(body)
    except ValueError as e:
        return

    if 'target' not in body or body['target'] != DEVICE_ID:
        return  # Not for me

    logging.info('Received push addressed to me: {}'.format(body))
    if 'exec' in body:
        logging.info('Executing command: {}'.format(body['exec']))
        os.system(body['exec'])


def on_push(ws, data):
    try:
        _on_push(ws, data)
    except Error as e:
        on_error(e)


def main():
    global DEBUG

    optlist, args = getopt(sys.argv[1:], 'vh')
    for opt, arg in optlist:
        if opt == '-v':
            DEBUG = True
        elif opt == '-h':
            print('''
Usage: {} [-v] [-h]
    -v  Enable debug mode
    -h  Show this help
'''.format(sys.argv[0]))
            return

    if DEBUG:
        logging.basicConfig(level=logging.DEBUG)
        websocket.enableTrace(True)
    else:
        logging.basicConfig(level=logging.INFO)

    ws = websocket.WebSocketApp('wss://stream.pushbullet.com/websocket/' +
                                API_KEY,
                                on_message = on_push,
                                on_error = on_error,
                                on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()


if __name__ == '__main__':
    main()

