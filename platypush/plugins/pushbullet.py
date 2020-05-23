import json
import os
from typing import Optional

import requests

from platypush.context import get_backend
from platypush.plugins import Plugin, action


class PushbulletPlugin(Plugin):
    """
    This plugin allows you to send pushes and files to your PushBullet account.
    Note: This plugin will only work if the :mod:`platypush.backend.pushbullet`
    backend is configured.

    Requires:

        * **requests** (``pip install requests``)
        * The :class:`platypush.backend.pushbullet.Pushbullet` backend enabled
    """

    def __init__(self, token: str = None, **kwargs):
        """
        :param token: Pushbullet API token. If not set the plugin will try to retrieve it from
            the Pushbullet backend configuration, if available
        """
        super().__init__(**kwargs)

        if not token:
            backend = get_backend('pushbullet')
            if not backend or not backend.token:
                raise AttributeError('No Pushbullet token specified')

            self.token = backend.token
        else:
            self.token = token

        self._devices = []
        self._devices_by_id = {}
        self._devices_by_name = {}

    @action
    def get_devices(self):
        """
        Get the list of available devices
        """
        resp = requests.get('https://api.pushbullet.com/v2/devices',
                            headers={'Authorization': 'Bearer ' + self.token,
                                     'Content-Type': 'application/json'})

        self._devices = resp.json().get('devices', [])
        self._devices_by_id = {
            dev['iden']: dev
            for dev in self._devices
        }

        self._devices_by_name = {
            dev['nickname']: dev
            for dev in self._devices if 'nickname' in dev
        }

    @action
    def get_device(self, device):
        """
        :param device: Device ID or name
        """
        output = None
        refreshed = False

        while not output:
            if device in self._devices_by_id:
                return self._devices_by_id[device]
            if device in self._devices_by_name:
                return self._devices_by_name[device]
            if refreshed:
                return None

            self.get_devices()
            refreshed = True

    @action
    def send_note(self, device: str = None, body: str = None, title: str = None, url: str = None, **kwargs):
        """
        Send a note push.

        :param device: Device ID or name (default: None, all devices)
        :param body: Note body
        :param title: Note title
        :param url: URL attached to the note
        :param kwargs: Push arguments, see https://docs.pushbullet.com/#create-push
        """

        if device:
            device = self.get_device(device).output
            if not device:
                raise RuntimeError('No such device')

        kwargs['body'] = body
        kwargs['title'] = title
        kwargs['type'] = 'link' if url else 'note'

        if device:
            kwargs['device_iden'] = device['iden']

        resp = requests.post('https://api.pushbullet.com/v2/pushes',
                             data=json.dumps(kwargs),
                             headers={'Authorization': 'Bearer ' + self.token,
                                      'Content-Type': 'application/json'})

        if resp.status_code >= 400:
            raise Exception('Pushbullet push failed with status {}: {}'.
                            format(resp.status_code, resp.json()))

    @action
    def send_file(self, filename: str, device: str = None):
        """
        Send a file.

        :param device: Device ID or name (default: None, all devices)
        :param filename: Path to the local file
        """

        if device:
            device = self.get_device(device).output
            if not device:
                raise RuntimeError('No such device')

        resp = requests.post('https://api.pushbullet.com/v2/upload-request',
                             data=json.dumps({'file_name': os.path.basename(filename)}),
                             headers={'Authorization': 'Bearer ' + self.token,
                                      'Content-Type': 'application/json'})

        if resp.status_code != 200:
            raise Exception('Pushbullet file upload request failed with status {}'.
                            format(resp.status_code))

        r = resp.json()
        resp = requests.post(r['upload_url'], data=r['data'],
                             files={'file': open(filename, 'rb')})

        if resp.status_code != 204:
            raise Exception('Pushbullet file upload failed with status {}'.
                            format(resp.status_code))

        resp = requests.post('https://api.pushbullet.com/v2/pushes',
                             headers={'Authorization': 'Bearer ' + self.token,
                                      'Content-Type': 'application/json'},

                             data=json.dumps({
                                 'type': 'file',
                                 'device_iden': device['iden'] if device else None,
                                 'file_name': r['file_name'],
                                 'file_type': r['file_type'],
                                 'file_url': r['file_url']}))

        if resp.status_code >= 400:
            raise Exception('Pushbullet file push failed with status {}'.
                            format(resp.status_code))

        return {
            'filename': r['file_name'],
            'type': r['file_type'],
            'url': r['file_url']
        }

    @action
    def send_clipboard(self, text: str):
        """
        Copy text to the clipboard of a device.

        :param text: Text to be copied.
        """
        backend = get_backend('pushbullet')
        device_id = backend.get_device_id() if backend else None

        resp = requests.post('https://api.pushbullet.com/v2/ephemerals',
                             data=json.dumps({
                                 'type': 'push',
                                 'push': {
                                     'body': text,
                                     'type': 'clip',
                                     'source_device_iden': device_id,
                                 },
                             }),
                             headers={'Authorization': 'Bearer ' + self.token,
                                      'Content-Type': 'application/json'})

        resp.raise_for_status()


# vim:sw=4:ts=4:et:
