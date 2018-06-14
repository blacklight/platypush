import json
import os
import requests

from platypush.context import get_backend
from platypush.message.response import Response
from platypush.plugins import Plugin


class PushbulletPlugin(Plugin):
    def send_push(self, **kwargs):
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

        return Response(output={'status':'ok'})


    def send_file(self, filename):
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

        return Response(output={
            'filename': r['file_name'],
            'type': r['file_type'],
            'url': r['file_url']
        })


# vim:sw=4:ts=4:et:

