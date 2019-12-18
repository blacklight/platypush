import json
import os
import requests

from requests.auth import HTTPBasicAuth
from typing import Optional, Union, Dict, List, Any

from platypush.message.response.camera.android import AndroidCameraStatusResponse, AndroidCameraStatusListResponse, \
    AndroidCameraPictureResponse
from platypush.plugins import Plugin, action


class AndroidIpcam:
    args = {}

    def __init__(self, name: str, host: str, port: int = 8080, username: Optional[str] = None,
                 password: Optional[str] = None, timeout: int = 10, ssl: bool = True):
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
        return json.dumps(getattr(self, 'args') or {})

    @property
    def base_url(self) -> str:
        return 'http{ssl}://{host}:{port}/'.format(
            ssl=('s' if self.ssl else ''), host=self.host, port=self.port)

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

    def __init__(self,
                 host: Optional[str] = None,
                 port: Optional[int] = 8080,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 timeout: int = 10,
                 ssl: bool = True,
                 cameras: Optional[Dict[str, Dict[str, Any]]] = None,
                 **kwargs):
        """
        :param host: Camera host name or address
        :param port: Camera port
        :param username: Camera username, if set
        :param password: Camera password, if set
        :param timeout: Connection timeout
        :param ssl: Use HTTPS instead of HTTP
        :param cameras: Alternatively, you can specify a list of IPCam cameras as a
            name->dict mapping. The keys will be unique names used to identify your
            cameras, the values will contain dictionaries containing `host, `port`,
            `username`, `password`, `timeout` and `ssl` attributes for each camera.
        """
        super().__init__(**kwargs)
        self.cameras: List[AndroidIpcam] = []
        self._camera_name_to_idx: Dict[str, int] = {}

        if not cameras:
            camera = AndroidIpcam(name=host, host=host, port=port, username=username,
                                  password=password, timeout=timeout, ssl=ssl)
            self.cameras.append(camera)
            self._camera_name_to_idx[host] = 0
        else:
            for name, camera in cameras.items():
                camera = AndroidIpcam(name=name, host=camera['host'], port=camera.get('port', port),
                                      username=camera.get('username'), password=camera.get('password'),
                                      timeout=camera.get('timeout', timeout), ssl=camera.get('ssl', ssl))
                self._camera_name_to_idx[name] = len(self.cameras)
                self.cameras.append(camera)

    def _get_camera(self, camera: Union[int, str] = None) -> AndroidIpcam:
        if not camera:
            camera = 0

        if isinstance(camera, int):
            return self.cameras[camera]

        return self.cameras[self._camera_name_to_idx[camera]]

    def _exec(self, url: str, camera: Union[int, str] = None, *args, **kwargs) -> Union[Dict[str, Any], bool]:
        cam = self._get_camera(camera)
        url = cam.base_url + url
        response = requests.get(url, auth=cam.auth, timeout=cam.timeout, verify=False, *args, **kwargs)
        response.raise_for_status()

        if response.headers.get('content-type') == 'application/json':
            return response.json()

        return response.text.find('Ok') != -1

    @action
    def change_setting(self, key: str, value: Union[str, int, bool], camera: Union[int, str] = None) -> bool:
        """
        Change a setting.
        :param key: Setting name
        :param value: Setting value
        :param camera: Camera index or configured name
        :return: True on success, False otherwise
        """
        if isinstance(value, bool):
            payload = "on" if value else "off"
        else:
            payload = value

        return self._exec("settings/{key}?set={payload}".format(key=key, payload=payload), camera=camera)

    @action
    def status(self, camera: Union[int, str] = None) -> AndroidCameraStatusListResponse:
        """
        :param camera: Camera index or name (default: status of all the cameras)
        :return: True if the camera is available, False otherwise
        """
        cameras = self._camera_name_to_idx.keys() if camera is None else [camera]
        statuses = []

        for c in cameras:
            try:
                if isinstance(camera, int):
                    cam = self.cameras[c]
                else:
                    cam = self.cameras[self._camera_name_to_idx[c]]

                status_data = self._exec('status.json', params={'show_avail': 1}, camera=cam.name).get('curvals', {})
                status = AndroidCameraStatusResponse(
                    name=cam.name,
                    stream_url=cam.stream_url,
                    image_url=cam.image_url,
                    audio_url=cam.audio_url,
                    **{k: v for k, v in status_data.items()
                       if k in AndroidCameraStatusResponse.attrs})

                statuses.append(status)
            except Exception as e:
                self.logger.warning('Could not get the status of {}: {}'.format(c, str(e)))

        return AndroidCameraStatusListResponse(statuses)

    @action
    def set_front_facing_camera(self, activate: bool = True, camera: Union[int, str] = None) -> bool:
        """Enable/disable the front-facing camera."""
        return self.change_setting('ffc', activate, camera=camera)

    @action
    def set_torch(self, activate: bool = True, camera: Union[int, str] = None) -> bool:
        """Enable/disable the torch."""
        url = 'enabletorch' if activate else 'disabletorch'
        return self._exec(url, camera=camera)

    @action
    def set_focus(self, activate: bool = True, camera: Union[int, str] = None) -> bool:
        """Enable/disable the focus."""
        url = 'focus' if activate else 'nofocus'
        return self._exec(url, camera=camera)

    @action
    def start_recording(self, tag: Optional[str] = None, camera: Union[int, str] = None) -> bool:
        """Start recording."""
        params = {'force': 1}
        if tag:
            params['tag'] = tag

        return self._exec('startvideo', params=params, camera=camera)

    @action
    def stop_recording(self, camera: Union[int, str] = None) -> bool:
        """Stop recording."""
        return self._exec('stopvideo', params={'force': 1}, camera=camera)

    @action
    def take_picture(self, image_file: str, camera: Union[int, str] = None) -> AndroidCameraPictureResponse:
        """Take a picture and save it on the local device."""
        cam = self._get_camera(camera)
        image_file = os.path.abspath(os.path.expanduser(image_file))
        os.makedirs(os.path.dirname(image_file), exist_ok=True)
        response = requests.get(cam.image_url, auth=cam.auth, verify=False)
        response.raise_for_status()

        with open(image_file, 'wb') as f:
            f.write(response.content)
        return AndroidCameraPictureResponse(image_file=image_file)

    @action
    def set_night_vision(self, activate: bool = True, camera: Union[int, str] = None) -> bool:
        """Enable/disable night vision."""
        return self.change_setting('night_vision', activate, camera=camera)

    @action
    def set_overlay(self, activate: bool = True, camera: Union[int, str] = None) -> bool:
        """Enable/disable video overlay."""
        return self.change_setting('overlay', activate, camera=camera)

    @action
    def set_gps(self, activate: bool = True, camera: Union[int, str] = None) -> bool:
        """Enable/disable GPS."""
        return self.change_setting('gps_active', activate, camera=camera)

    @action
    def set_quality(self, quality: int = 100, camera: Union[int, str] = None) -> bool:
        """Set video quality."""
        return self.change_setting('quality', int(quality), camera=camera)

    @action
    def set_motion_detect(self, activate: bool = True, camera: Union[int, str] = None) -> bool:
        """Enable/disable motion detect."""
        return self.change_setting('motion_detect', activate, camera=camera)

    @action
    def set_orientation(self, orientation: str = 'landscape', camera: Union[int, str] = None) -> bool:
        """Set video orientation."""
        return self.change_setting('orientation', orientation, camera=camera)

    @action
    def set_zoom(self, zoom: float, camera: Union[int, str] = None) -> bool:
        """Set the zoom level."""
        return self._exec('settings/ptz', params={'zoom': float(zoom)}, camera=camera)

    @action
    def set_scenemode(self, scenemode: str = 'auto', camera: Union[int, str] = None) -> bool:
        """Set video orientation."""
        return self.change_setting('scenemode', scenemode, camera=camera)


# vim:sw=4:ts=4:et:
