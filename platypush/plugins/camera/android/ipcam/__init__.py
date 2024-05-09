import json
import os
import requests

from requests.auth import HTTPBasicAuth
from typing import Optional, Sequence, Union, Dict, List, Any

from platypush.plugins import Plugin, action
from platypush.schemas.camera.android.ipcam import CameraStatusSchema


class AndroidIpcam:
    """
    IPCam camera configuration.
    """

    args = {}

    def __init__(
        self,
        name: str,
        host: str,
        port: int = 8080,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 10,
        ssl: bool = True,
    ):
        self.args = {
            'name': name,
            'host': host,
            'port': port,
            'username': username,
            'password': password,
            'timeout': timeout,
            'ssl': ssl,
        }

        self.auth = None
        if username:
            self.auth = HTTPBasicAuth(self.username, self.password)

    def __getattr__(self, item):
        if item in self.args:
            return super().__getattribute__('args').get(item)
        return super().__getattribute__(item)

    def __setattr__(self, key, value):
        if key not in self.args:
            super().__setattr__(key, value)
        else:
            self.args[key] = value

    def __str__(self):
        return json.dumps(self.args or {})

    @property
    def base_url(self) -> str:
        return 'http{ssl}://{host}:{port}/'.format(
            ssl=('s' if self.ssl else ''), host=self.host, port=self.port
        )

    @property
    def stream_url(self) -> str:
        return self.base_url + 'video'

    @property
    def audio_url(self) -> str:
        return self.base_url + 'audio.wav'

    @property
    def image_url(self) -> str:
        return self.base_url + 'photo.jpg'


class CameraAndroidIpcamPlugin(Plugin):
    """
    Plugin to control remote Android cameras over
    `IPCam <https://play.google.com/store/apps/details?id=com.pas.webcam>`_.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        host: Optional[str] = None,
        port: int = 8080,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 10,
        ssl: bool = True,
        cameras: Optional[Sequence[dict]] = None,
        **kwargs,
    ):
        """
        :param name: Custom name for the default camera (default: IP/hostname)
        :param host: Camera host name or address
        :param port: Camera port
        :param username: Camera username, if set
        :param password: Camera password, if set
        :param timeout: Connection timeout
        :param ssl: Use HTTPS instead of HTTP
        :param cameras: Alternatively, you can specify a list of IPCam cameras as a
            list of objects with ``name``, ``host``, ``port``, ``username``,
            ``password``, ``timeout`` and ``ssl`` attributes.
        """
        super().__init__(**kwargs)
        self.cameras: List[AndroidIpcam] = []
        self._camera_name_to_idx: Dict[str, int] = {}

        if not cameras:
            assert host, 'You need to specify at least one camera'
            name = name or host
            camera = AndroidIpcam(
                name=name,
                host=host,
                port=port,
                username=username,
                password=password,
                timeout=timeout,
                ssl=ssl,
            )
            self.cameras.append(camera)
            self._camera_name_to_idx[name] = 0
        else:
            for camera in cameras:
                assert 'host' in camera, 'You need to specify the host for each camera'
                name = camera.get('name', camera['host'])
                camera = AndroidIpcam(
                    name=name,
                    host=camera['host'],
                    port=camera.get('port', port),
                    username=camera.get('username'),
                    password=camera.get('password'),
                    timeout=camera.get('timeout', timeout),
                    ssl=camera.get('ssl', ssl),
                )
                self._camera_name_to_idx[name] = len(self.cameras)
                self.cameras.append(camera)

    def _get_camera(self, camera: Optional[Union[int, str]] = None) -> AndroidIpcam:
        if not camera:
            camera = 0

        if isinstance(camera, int):
            return self.cameras[camera]

        return self.cameras[self._camera_name_to_idx[camera]]

    def _exec(
        self, url: str, *args, camera: Optional[Union[int, str]] = None, **kwargs
    ) -> Union[Dict[str, Any], bool]:
        cam = self._get_camera(camera)
        url = cam.base_url + url
        response = requests.get(
            url, auth=cam.auth, timeout=cam.timeout, verify=False, *args, **kwargs
        )
        response.raise_for_status()

        if response.headers.get('content-type') == 'application/json':
            return response.json()

        return response.text.find('Ok') != -1

    def _change_setting(
        self,
        key: str,
        value: Union[str, int, bool],
        camera: Optional[Union[int, str]] = None,
    ) -> bool:
        if isinstance(value, bool):
            payload = "on" if value else "off"
        else:
            payload = value

        return bool(
            self._exec(
                "settings/{key}?set={payload}".format(key=key, payload=payload),
                camera=camera,
            )
        )

    @action
    def change_setting(
        self,
        key: str,
        value: Union[str, int, bool],
        camera: Optional[Union[int, str]] = None,
    ) -> bool:
        """
        Change a setting.

        :param key: Setting name
        :param value: Setting value
        :param camera: Camera index or configured name
        :return: True on success, False otherwise
        """
        return self._change_setting(key, value, camera=camera)

    @action
    def status(self, camera: Optional[Union[int, str]] = None) -> List[dict]:
        """
        :param camera: Camera index or name (default: status of all the cameras)
        :return: .. schema:: camera.android.ipcam.CameraStatusSchema(many=True)
        """
        cameras = self._camera_name_to_idx.keys() if camera is None else [camera]
        statuses = []

        for c in cameras:
            try:
                print('****** HERE ******')
                print(self._camera_name_to_idx)
                if isinstance(c, int):
                    cam = self.cameras[c]
                else:
                    cam = self.cameras[self._camera_name_to_idx[c]]

                response = self._exec(
                    'status.json', params={'show_avail': 1}, camera=cam.name
                )
                assert isinstance(response, dict), f'Invalid response: {response}'

                status_data = response.get('curvals', {})
                status = CameraStatusSchema().dump(
                    {
                        'name': cam.name,
                        'stream_url': cam.stream_url,
                        'image_url': cam.image_url,
                        'audio_url': cam.audio_url,
                        **status_data,
                    }
                )

                statuses.append(status)
            except Exception as e:
                self.logger.warning(
                    'Could not get the status of %s: %s: %s', c, type(e), e
                )

        return statuses

    @action
    def set_front_facing_camera(
        self, activate: bool = True, camera: Optional[Union[int, str]] = None
    ) -> bool:
        """Enable/disable the front-facing camera."""
        return self._change_setting('ffc', activate, camera=camera)

    @action
    def set_torch(
        self, activate: bool = True, camera: Optional[Union[int, str]] = None
    ) -> bool:
        """Enable/disable the torch."""
        url = 'enabletorch' if activate else 'disabletorch'
        return bool(self._exec(url, camera=camera))

    @action
    def set_focus(
        self, activate: bool = True, camera: Optional[Union[int, str]] = None
    ) -> bool:
        """Enable/disable the focus."""
        url = 'focus' if activate else 'nofocus'
        return bool(self._exec(url, camera=camera))

    @action
    def start_recording(
        self, tag: Optional[str] = None, camera: Optional[Union[int, str]] = None
    ) -> bool:
        """Start recording."""
        params = {
            'force': 1,
            **({'tag': tag} if tag else {}),
        }
        return bool(self._exec('startvideo', params=params, camera=camera))

    @action
    def stop_recording(self, camera: Optional[Union[int, str]] = None) -> bool:
        """Stop recording."""
        return bool(self._exec('stopvideo', params={'force': 1}, camera=camera))

    @action
    def take_picture(
        self, image_file: str, camera: Optional[Union[int, str]] = None
    ) -> dict:
        """
        Take a picture and save it on the local device.

        :return: dict

          .. code-block:: json

            {
              "image_file": "/path/to/image.jpg"
            }

        """
        cam = self._get_camera(camera)
        image_file = os.path.abspath(os.path.expanduser(image_file))
        os.makedirs(os.path.dirname(image_file), exist_ok=True)
        response = requests.get(cam.image_url, auth=cam.auth, verify=False)
        response.raise_for_status()

        with open(image_file, 'wb') as f:
            f.write(response.content)

        return {'image_file': image_file}

    @action
    def set_night_vision(
        self, activate: bool = True, camera: Optional[Union[int, str]] = None
    ) -> bool:
        """Enable/disable night vision."""
        return self._change_setting('night_vision', activate, camera=camera)

    @action
    def set_overlay(
        self, activate: bool = True, camera: Optional[Union[int, str]] = None
    ) -> bool:
        """Enable/disable video overlay."""
        return self._change_setting('overlay', activate, camera=camera)

    @action
    def set_gps(
        self, activate: bool = True, camera: Optional[Union[int, str]] = None
    ) -> bool:
        """Enable/disable GPS."""
        return self._change_setting('gps_active', activate, camera=camera)

    @action
    def set_quality(
        self, quality: int = 100, camera: Optional[Union[int, str]] = None
    ) -> bool:
        """Set video quality."""
        return self._change_setting('quality', int(quality), camera=camera)

    @action
    def set_motion_detect(
        self, activate: bool = True, camera: Optional[Union[int, str]] = None
    ) -> bool:
        """Enable/disable motion detect."""
        return self._change_setting('motion_detect', activate, camera=camera)

    @action
    def set_orientation(
        self, orientation: str = 'landscape', camera: Optional[Union[int, str]] = None
    ) -> bool:
        """Set video orientation."""
        return self._change_setting('orientation', orientation, camera=camera)

    @action
    def set_zoom(self, zoom: float, camera: Optional[Union[int, str]] = None) -> bool:
        """Set the zoom level."""
        return bool(
            self._exec('settings/ptz', params={'zoom': float(zoom)}, camera=camera)
        )

    @action
    def set_scenemode(
        self, scenemode: str = 'auto', camera: Optional[Union[int, str]] = None
    ) -> bool:
        """Set video orientation."""
        return self._change_setting('scenemode', scenemode, camera=camera)


# vim:sw=4:ts=4:et:
