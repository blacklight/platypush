from dataclasses import dataclass
import json
import os
import time
from enum import Enum
from threading import Event, RLock
from typing import Optional, Type

import requests

from platypush.config import Config
from platypush.message.event.pushbullet import (
    PushbulletDismissalEvent,
    PushbulletEvent,
    PushbulletFileEvent,
    PushbulletLinkEvent,
    PushbulletMessageEvent,
    PushbulletNotificationEvent,
)
from platypush.plugins import RunnablePlugin, action
from platypush.schemas.pushbullet import PushbulletDeviceSchema, PushbulletSchema


class PushbulletType(Enum):
    """
    PushBullet event types.
    """

    DISMISSAL = 'dismissal'
    FILE = 'file'
    LINK = 'link'
    MESSAGE = 'message'
    MIRROR = 'mirror'
    NOTE = 'note'


@dataclass
class PushbulletEventType:
    """
    PushBullet event type.
    """

    type: PushbulletType
    event_class: Type[PushbulletEvent]


_push_event_types = [
    PushbulletEventType(
        type=PushbulletType.DISMISSAL,
        event_class=PushbulletDismissalEvent,
    ),
    PushbulletEventType(
        type=PushbulletType.FILE,
        event_class=PushbulletFileEvent,
    ),
    PushbulletEventType(
        type=PushbulletType.LINK,
        event_class=PushbulletLinkEvent,
    ),
    PushbulletEventType(
        type=PushbulletType.MESSAGE,
        event_class=PushbulletMessageEvent,
    ),
    PushbulletEventType(
        type=PushbulletType.MIRROR,
        event_class=PushbulletNotificationEvent,
    ),
    PushbulletEventType(
        type=PushbulletType.NOTE,
        event_class=PushbulletMessageEvent,
    ),
]

_push_events_by_type = {t.type.value: t for t in _push_event_types}


class PushbulletPlugin(RunnablePlugin):
    """
    `PushBullet <https://www.pushbullet.com/>`_ integration.

    Among the other things, this plugin allows you to easily interact with your
    mobile devices that have the app installed from Platypush.

    If notification mirroring is enabled on your device, then the push
    notifications will be mirrored to Platypush as well as PushBullet events.

    Since PushBullet also comes with a Tasker integration, you can also use this
    plugin to send commands to your Android device and trigger actions on it.
    It can be used to programmatically send files to your devices and manage
    shared clipboards too.
    """

    _timeout = 15.0
    _upload_timeout = 600.0

    def __init__(
        self,
        token: str,
        device: Optional[str] = None,
        enable_mirroring: bool = True,
        **kwargs,
    ):
        """
        :param token: PushBullet API token, see https://docs.pushbullet.com/#authentication.
        :param device: Device ID that should be exposed. Default: ``Platypush @
            <device_id | hostname>``.
        :param enable_mirroring: If set to True (default) then the plugin will
            receive notifications mirrored from other connected devices -
            these will also be rendered on the connected web clients. Disable
            it if you don't want to forward your mobile notifications through
            the plugin.
        """
        super().__init__(**kwargs)

        if not device:
            device = f'Platypush @ {Config.get_device_id()}'

        self.token = token
        self.device_name = device
        self.enable_mirroring = enable_mirroring
        self.listener = None
        self._initialized = Event()
        self._device = None
        self._init_lock = RLock()
        self._pb = None
        self._device_id = None
        self._devices = []
        self._devices_by_id = {}
        self._devices_by_name = {}

    def _initialize(self):
        from pushbullet import Pushbullet

        if self._initialized.is_set():
            return

        self._pb = Pushbullet(self.token)

        try:
            self._device = self._pb.get_device(self.device_name)
        except Exception as e:
            self.logger.info(
                'Device %s does not exist: %s. Creating it',
                self.device_name,
                e,
            )
            self._device = self._pb.new_device(self.device_name)

        self._device_id = self.get_device_id()
        self._initialized.set()

    @property
    def pb(self):
        """
        :return: PushBullet API object.
        """
        with self._init_lock:
            self._initialize()

        assert self._pb
        return self._pb

    @property
    def device(self):
        """
        :return: Current PushBullet device object.
        """
        with self._init_lock:
            self._initialize()

        assert self._device
        return self._device

    @property
    def device_id(self):
        return self.device.device_iden

    def _request(self, method: str, url: str, **kwargs):
        meth = getattr(requests, method)
        resp = meth(
            'https://api.pushbullet.com/v2/' + url.lstrip('/'),
            timeout=self._timeout,
            headers={
                'Authorization': 'Bearer ' + self.token,
                'Content-Type': 'application/json',
            },
            **kwargs,
        )

        resp.raise_for_status()
        return resp.json()

    def get_device_id(self):
        assert self._pb

        try:
            return self._pb.get_device(self.device_name).device_iden
        except Exception:
            device = self.pb.new_device(
                self.device_name,
                model='Platypush virtual device',
                manufacturer='platypush',
                icon='system',
            )

            self.logger.info('Created Pushbullet device %s', self.device_name)
            return device.device_iden

    def _get_latest_push(self):
        t = int(time.time()) - 10
        pushes = self.pb.get_pushes(modified_after=str(t), limit=1)
        if pushes:
            return pushes[0]

        return None

    def on_open(self, *_, **__):
        self.logger.info('Pushbullet connected')

    def on_close(self, args=None):
        err = args[0] if args else None
        self.close()
        assert not err or self.should_stop(), 'Pushbullet connection closed: ' + str(
            err or 'unknown error'
        )

    def on_error(self, *args):
        raise RuntimeError('Pushbullet error: ' + str(args))

    def on_push(self, data):
        try:
            # Parse the push
            try:
                data = json.loads(data) if isinstance(data, str) else data
            except Exception as e:
                self.logger.exception(e)
                return

            # If it's a push, get it
            push = None
            if data['type'] == 'tickle' and data['subtype'] == 'push':
                push = self._get_latest_push()
            elif data['type'] == 'push':
                push = data['push']

            if not push:
                self.logger.debug('Not a push notification.\nMessage: %s', data)
                return

            push_type = push.pop('type', None)
            push_event_type = _push_events_by_type.get(push_type)
            if not push_event_type:
                self.logger.debug(
                    'Unknown push type: %s.\nMessage: %s', push_type, data
                )
                return

            if (
                not self.enable_mirroring
                and push_event_type.type == PushbulletType.MIRROR
            ):
                return

            push = dict(PushbulletSchema().dump(push))
            evt_type = push_event_type.event_class
            self._bus.post(evt_type(**push))
        except Exception as e:
            self.logger.warning(
                'Error while processing push: %s.\nMessage: %s', e, data
            )
            self.logger.exception(e)
            return

    def _get_device(self, device) -> Optional[dict]:
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

        return None

    def close(self):
        if self.listener:
            try:
                self.listener.close()
            except Exception:
                pass

            self.listener = None

        if self._pb:
            self._pb = None

        self._initialized.clear()

    def run_listener(self):
        from .listener import Listener

        self.listener = Listener(
            account=self.pb,
            on_push=self.on_push,
            on_open=self.on_open,
            on_close=self.on_close,
            on_error=self.on_error,
        )

        self.listener.run_forever()

    @action
    def get_devices(self):
        """
        Get the list of available devices.

        :return: .. schema:: pushbullet.PushbulletDeviceSchema(many=True)
        """
        resp = self._request('get', 'devices')
        self._devices = resp.get('devices', [])
        self._devices_by_id = {dev['iden']: dev for dev in self._devices}
        self._devices_by_name = {
            dev['nickname']: dev for dev in self._devices if 'nickname' in dev
        }

        return PushbulletDeviceSchema(many=True).dump(self._devices)

    @action
    def get_device(self, device: str) -> Optional[dict]:
        """
        Get a device by ID or name.

        :param device: Device ID or name
        :return: .. schema:: pushbullet.PushbulletDeviceSchema
        """
        dev = self._get_device(device)
        if not dev:
            return None

        return dict(PushbulletDeviceSchema().dump(dev))

    @action
    def get_pushes(self, limit: int = 10):
        """
        Get the list of pushes.

        :param limit: Maximum number of pushes to fetch (default: 10).
        :return: .. schema:: pushbullet.PushbulletSchema(many=True)
        """
        return PushbulletSchema().dump(
            self._request('get', 'pushes', params={'limit': limit}).get('pushes', []),
            many=True,
        )

    @action
    def send_note(
        self,
        device: Optional[str] = None,
        body: Optional[str] = None,
        title: Optional[str] = None,
        url: Optional[str] = None,
        **kwargs,
    ):
        """
        Send a note push.

        :param device: Device ID or name (default: None, all devices)
        :param body: Note body
        :param title: Note title
        :param url: URL attached to the note
        :param kwargs: Push arguments, see https://docs.pushbullet.com/#create-push
        :return: .. schema:: pushbullet.PushbulletSchema
        """

        dev = None
        if device:
            dev = self._get_device(device)
            assert dev, f'No such device: {device}'

        kwargs['body'] = body
        kwargs['title'] = title
        kwargs['type'] = 'note'
        if url:
            kwargs['type'] = 'link'
            kwargs['url'] = url

        if dev:
            kwargs['device_iden'] = dev['iden']

        rs = self._request('post', 'pushes', data=json.dumps(kwargs))
        return dict(PushbulletSchema().dump(rs))

    @action
    def send_file(self, filename: str, device: Optional[str] = None):
        """
        Send a file.

        :param device: Device ID or name (default: None, all devices)
        :param filename: Path to the local file
        """

        dev = None
        if device:
            dev = self._get_device(device)
            assert dev, f'No such device: {device}'

        upload_req = self._request(
            'post',
            'upload-request',
            data=json.dumps({'file_name': os.path.basename(filename)}),
        )

        with open(filename, 'rb') as f:
            rs = requests.post(
                upload_req['upload_url'],
                data=upload_req['data'],
                files={'file': f},
                timeout=self._upload_timeout,
            )

        rs.raise_for_status()
        self._request(
            'post',
            'pushes',
            data=json.dumps(
                {
                    'type': 'file',
                    'device_iden': dev['iden'] if dev else None,
                    'file_name': upload_req['file_name'],
                    'file_type': upload_req.get('file_type'),
                    'file_url': upload_req['file_url'],
                }
            ),
        )

        return {
            'filename': upload_req['file_name'],
            'type': upload_req.get('file_type'),
            'url': upload_req['file_url'],
        }

    @action
    def send_clipboard(self, text: str):
        """
        Send text to the clipboard of other devices.

        :param text: Text to be copied.
        """
        self._request(
            'post',
            'ephemerals',
            data=json.dumps(
                {
                    'type': 'push',
                    'push': {
                        'body': text,
                        'type': 'clip',
                        'source_device_iden': self.device_id,
                    },
                }
            ),
        )

    def main(self):
        while not self.should_stop():
            while not self._initialized.is_set():
                try:
                    self._initialize()
                except Exception as e:
                    self.logger.exception(e)
                    self.logger.error('Pushbullet initialization error: %s', e)
                    self.wait_stop(10)

            while not self.should_stop():
                try:
                    self.run_listener()
                except Exception as e:
                    if not self.should_stop():
                        self.logger.exception(e)
                        self.logger.error('Pushbullet listener error: %s', e)

                    self.wait_stop(10)


# vim:sw=4:ts=4:et:
