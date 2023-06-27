from enum import Enum
import json
from typing import Optional
from typing_extensions import override

from tornado.web import stream_request_body
from platypush.context import get_plugin

from platypush.config import Config
from platypush.plugins.camera import Camera, CameraPlugin, StreamWriter
from platypush.utils import get_plugin_name_by_class

from .. import StreamingRoute


class RequestType(Enum):
    """
    Models the camera route request type (video or photo)
    """

    UNKNOWN = ''
    PHOTO = 'photo'
    VIDEO = 'video'


@stream_request_body
class CameraRoute(StreamingRoute):
    """
    Route for camera streams.
    """

    _redis_queue_prefix = f'_platypush/{Config.get("device_id") or ""}/camera'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._camera: Optional[Camera] = None
        self._request_type = RequestType.UNKNOWN
        self._extension: str = ''

    @override
    @classmethod
    def path(cls) -> str:
        return r"/camera/([a-zA-Z0-9_./]+)/([a-zA-Z0-9_]+)\.?([a-zA-Z0-9_]+)?"

    def _get_camera(self, plugin: str) -> CameraPlugin:
        plugin_name = f'camera.{plugin.replace("/", ".")}'
        p = get_plugin(plugin_name)
        assert p, f'No such plugin: {plugin_name}'
        return p

    def _get_frame(
        self, camera: Camera, timeout: Optional[float] = None
    ) -> Optional[bytes]:
        if camera.stream:
            with camera.stream.ready:
                camera.stream.ready.wait(timeout=timeout)
                return camera.stream.frame

        return None

    def send_frame(self, camera: Camera):
        frame = None
        for _ in range(camera.info.warmup_frames):
            frame = self._get_frame(camera)

        if frame:
            self.write(frame)
            self.flush()

    def _set_request_type_and_extension(self, route: str, extension: str):
        if route in {'photo', 'frame'}:
            self._request_type = RequestType.PHOTO
            if extension == 'jpg':
                extension = 'jpeg'
            self._extension = extension or 'jpeg'
        elif route in {'video', 'feed'}:
            self._request_type = RequestType.VIDEO
            self._extension = extension or 'mjpeg'

    def _get_args(self, kwargs: dict):
        kwargs = {k: v[0].decode() for k, v in kwargs.items() if k != 't'}
        for k, v in kwargs.items():
            if k == 'resolution':
                v = json.loads(f'[{v}]')
            else:
                try:
                    v = int(v)
                except (ValueError, TypeError):
                    try:
                        v = float(v)
                    except (ValueError, TypeError):
                        pass

            kwargs[k] = v

        return kwargs

    @override
    @classmethod
    def _get_redis_queue(cls, camera: CameraPlugin, *_, **__) -> str:
        plugin_name = get_plugin_name_by_class(camera.__class__)
        assert plugin_name, f'No such plugin: {plugin_name}'
        return '/'.join(
            [
                cls._redis_queue_prefix,
                plugin_name,
                *map(
                    str,
                    [camera.camera_info.device] if camera.camera_info.device else [],
                ),
            ]
        )

    def get(self, plugin: str, route: str, extension: str = '') -> None:
        self._set_request_type_and_extension(route, extension)
        if not (self._request_type and self._extension):
            self.write_error(404, 'Not Found')
            return

        stream_class = StreamWriter.get_class_by_name(self._extension)
        camera = self._get_camera(plugin)
        redis_queue = self._get_redis_queue(camera)
        self.set_header('Content-Type', stream_class.mimetype)

        with camera.open(
            stream=True,
            stream_format=self._extension,
            frames_dir=None,
            redis_queue=redis_queue,
            **self._get_args(self.request.arguments),
        ) as session:
            camera.start_camera(session)
            if self._request_type == RequestType.PHOTO:
                self.send_frame(session)
            elif self._request_type == RequestType.VIDEO:
                self.forward_stream(camera)

        self.finish()
