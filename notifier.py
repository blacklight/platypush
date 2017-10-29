#!/usr/bin/env python

import os
import logging
import json
import subprocess

from pushbullet import Listener
from pushbullet import Pushbullet

__author__ = 'Fabio Manganiello <info@fabiomanganiello.com>'

def get_hostname():
    with open('/etc/hostname','r') as fp:
        return fp.readline().strip()

logging.basicConfig(level=logging.INFO)
hostname = get_hostname()

API_KEY = 'o.EHMMnZneJdpNQv9FSFbyY2busin7floe'
HTTP_PROXY_HOST = None
HTTP_PROXY_PORT = None


def on_push(data):
    global hostname

    if 'type' not in data \
            or 'push' not in data \
            or data['type'] != 'push':
        return  # Not a push notification

    push = data['push']
    logging.debug('Received push: {}'.format(push))

    if 'body' not in push:
        return

    body = None
    try:
        body = json.loads(push['body'])
    except ValueError as e:
        return

    if 'target' not in body or body['target'] != hostname:
        return  # Not for me

    logging.info('Received message: {}'.format(body))
    if 'cmd' in body:
        logging.info('Executing command: {}'.format(body['cmd']))
        os.system(body['cmd'])


def main():
    pb = Pushbullet(API_KEY)

    s = Listener(account=pb,
                 on_push=on_push,
                 http_proxy_host=HTTP_PROXY_HOST,
                 http_proxy_port=HTTP_PROXY_PORT)
    try:
        s.run_forever()
    except KeyboardInterrupt:
        s.close()


if __name__ == '__main__':
    main()
