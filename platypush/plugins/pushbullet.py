import json
import os
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
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @action
    def send_push(self, **kwargs):
        """
        Send a push.

        :param kwargs: Push arguments, see https://docs.pushbullet.com/#create-push
        :type kwargs: dict
        """

        pushbullet = get_backend('pushbullet')
        resp = requests.post('https://api.pushbullet.com/v2/ephemerals',
                             data=json.dumps({
                                 'type':'push',
                                 'push': kwargs,
                             }),

                             headers={'Authorization': 'Bearer ' + pushbullet.token,
                                      'Content-Type': 'application/json'})

        if resp.status_code >= 400:
            raise Exception('Pushbullet push failed with status {}: {}'.
                            format(resp.status_code, resp.json()))


    @action
    def send_file(self, filename):
        """
        Send a file.

        :param filename: Path to the local file
        :type filename: str
        """

        pushbullet = get_backend('pushbullet')
        resp = requests.post('https://api.pushbullet.com/v2/upload-request',
                             data=json.dumps({'file_name': os.path.basename(filename)}),
                             headers={'Authorization': 'Bearer ' + pushbullet.token,
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
                             headers={'Authorization': 'Bearer ' + pushbullet.token,
                                      'Content-Type': 'application/json'},

                             data=json.dumps({
                                 'type': 'file',
                                 'file_name': r['file_name'],
                                 'file_type': r['file_type'],
                                 'file_url': r['file_url'] }))

        if resp.status_code >= 400:
            raise Exception('Pushbullet file push failed with status {}'.
                            format(resp.status_code))

        return {
            'filename': r['file_name'],
            'type': r['file_type'],
            'url': r['file_url']
        }


# vim:sw=4:ts=4:et:

