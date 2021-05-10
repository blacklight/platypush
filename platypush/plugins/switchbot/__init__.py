import queue
import requests
import threading
from typing import List, Optional, Union

from platypush.plugins import action
from platypush.plugins.switch import SwitchPlugin
from platypush.schemas.switchbot import DeviceSchema, DeviceStatusSchema, SceneSchema


class SwitchbotPlugin(SwitchPlugin):
    """
    Plugin to interact with the devices registered to a Switchbot (https://www.switch-bot.com/) account/hub.

    The difference between this plugin and :class:`platypush.plugins.switchbot.bluetooth.SwitchbotBluetoothPlugin` is
    that the latter acts like a Bluetooth hub/bridge that interacts directly with your Switchbot devices, while this
    plugin requires the devices to be connected to a Switchbot Hub and it controls them through your cloud account.

    In order to use this plugin:

        - Set up a Switchbot Hub and configure your devices through the Switchbot app.
        - Follow the steps on the `Switchbot API repo <https://github.com/OpenWonderLabs/SwitchBotAPI#getting-started>`_
          to get an API token from the app.

    """

    def __init__(self, api_token: str, **kwargs):
        """
        :param api_token: API token (see
            `Getting started with the Switchbot API <https://github.com/OpenWonderLabs/SwitchBotAPI#getting-started>`_).
        """
        super().__init__(**kwargs)
        self._api_token = api_token
        self._devices_by_id = {}
        self._devices_by_name = {}

    @staticmethod
    def _url_for(*args, device=None):
        url = 'https://api.switch-bot.com/v1.0/'
        if device:
            url += f'devices/{device["id"]}/'
        url += '/'.join(args)
        return url

    def _run(self, method: str = 'get', *args, device=None, **kwargs):
        response = getattr(requests, method)(self._url_for(*args, device=device), headers={
            'Authorization': self._api_token,
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=utf-8',
        }, **kwargs)

        response.raise_for_status()
        response = response.json()
        assert response.get('statusCode') == 100, \
            f'Switchbot API request failed: {response.get("statusCode")}: {response.get("message")}'

        return response.get('body')

    def _get_device(self, device: str, use_cache=True):
        if not use_cache:
            self.devices()

        if device in self._devices_by_id:
            return self._devices_by_id[device]
        if device in self._devices_by_name:
            return self._devices_by_name[device]

        assert use_cache, f'Device not found: {device}'
        return self._get_device(device, use_cache=False)

    @action
    def devices(self) -> List[dict]:
        """
        Get the list of devices associated to the specified Switchbot API account.

        :return: .. schema:: switchbot.DeviceSchema(many=True)
        """
        devices = DeviceSchema().dump(self._run('get', 'devices').get('deviceList', []), many=True)
        for device in devices:
            self._devices_by_id[device['id']] = device
            self._devices_by_name[device['name']] = device

        return devices

    def _worker(self, q: queue.Queue, method: str = 'get', *args, device=None, **kwargs):
        try:
            res = self._run(method, *args, device=device, **kwargs)
            q.put(DeviceStatusSchema().dump(res))
        except Exception as e:
            self.logger.exception(e)
            q.put(e)

    @action
    def status(self, device: Optional[str] = None) -> Union[dict, List[dict]]:
        """
        Get the status of all the registered devices or of a specific device.

        :param device: Filter by device ID or name.
        :return: .. schema:: switchbot.DeviceStatusSchema(many=True)
        """
        # noinspection PyUnresolvedReferences
        devices = self.devices().output
        if device:
            return {
                **device,
                **self._run('get', 'status', device=self._get_device(device)),
            }

        devices_by_id = {dev['id']: dev for dev in devices}
        queues = [queue.Queue()] * len(devices)
        workers = [
            threading.Thread(target=self._worker, args=(queues[i], 'get', 'status'), kwargs={'device': dev})
            for i, dev in enumerate(devices)
        ]

        results = []
        for worker in workers:
            worker.start()

        for q in queues:
            response = q.get()
            if not response:
                continue

            assert not isinstance(response, Exception), str(response)
            results.append({
                **devices_by_id.get(response.get('id'), {}),
                **response,
            })
        for worker in workers:
            worker.join()

        return results

    @action
    def press(self, device: str):
        """
        Send a press-button command to a device.

        :param device: Device name or ID.
        """
        device = self._get_device(device)
        return self._run('post', 'commands', device=device, json={'command': 'press'})

    @action
    def toggle(self, device: str, **kwargs):
        """
        Shortcut for :meth:`.press`.

        :param device: Device name or ID.
        """
        return self.press(device)

    @action
    def on(self, device: str, **kwargs):
        """
        Send a turn-on command to a device

        :param device: Device name or ID.
        """
        device = self._get_device(device)
        return self._run('post', 'commands', device=device, json={'command': 'turnOn'})

    @action
    def off(self, device: str, **kwargs):
        """
        Send a turn-off command to a device

        :param device: Device name or ID.
        """
        device = self._get_device(device)
        return self._run('post', 'commands', device=device, json={'command': 'turnOff'})

    @property
    def switches(self) -> List[dict]:
        # noinspection PyUnresolvedReferences
        return [
            dev for dev in self.status().output if 'on' in dev
        ]

    @action
    def set_curtain_position(self, device: str, position: int):
        """
        Set the position of a curtain device.

        :param device: Device name or ID.
        :param position: An integer between 0 (open) and 100 (closed).
        """
        device = self._get_device(device)
        return self._run('post', 'commands', device=device, json={
            'command': 'setPosition',
            'commandType': 'command',
            'parameter': f'0,ff,{position}',
        })

    @action
    def set_humidifier_efficiency(self, device: str, efficiency: Union[int, str]):
        """
        Set the nebulization efficiency of a humidifier device.

        :param device: Device name or ID.
        :param efficiency: An integer between 0 (open) and 100 (closed) or `auto`.
        """
        device = self._get_device(device)
        return self._run('post', 'commands', device=device, json={
            'command': 'setMode',
            'commandType': 'command',
            'parameter': efficiency,
        })

    @action
    def set_fan(self, device: str, speed: Optional[int] = None, swing_range: Optional[int] = None,
                mode: Optional[int] = None):
        """
        Set properties of a smart fan device.

        :param device: Device name or ID.
        :param speed: Speed between 1 and 4.
        :param swing_range: Swing range angle, between 0 and 120.
        :param mode: Fan mode (1 or 2).
        """
        # noinspection PyUnresolvedReferences
        status = self.status(device=device).output

        if speed is None:
            speed = status.get('speed')
        if mode is None:
            mode = status.get('mode')
        if swing_range is None:
            swing_range = status.get('swing_range')

        return self._run('post', 'commands', device=device, json={
            'command': 'set',
            'commandType': 'command',
            'parameter': ','.join(['on', str(mode), str(speed), str(swing_range)]),
        })

    @action
    def scenes(self) -> List[dict]:
        """
        Get the list of registered scenes.

        :return: .. schema:: switchbot.SceneSchema(many=True)
        """
        return SceneSchema().dump(self._run('get', 'scenes'), many=True)

    @action
    def run_scene(self, scene: str):
        """
        Execute a scene.

        :param scene: Scene ID or name.
        """
        # noinspection PyUnresolvedReferences
        scenes = [
            s for s in self.scenes().output
            if s.get('id') == scene or s.get('name') == scene
        ]

        assert scenes, f'No such scene: {scene}'
        return self._run('post', 'scenes', scenes[0]['id'], 'execute')


# vim:sw=4:ts=4:et:
