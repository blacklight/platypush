from enum import Enum
import json
from logging import getLogger
from typing import Optional
from typing_extensions import override

from tornado.web import stream_request_body
from platypush.context import get_plugin

from platypush.plugins.camera import Camera, CameraPlugin, StreamWriter

from .. import StreamingRoute

logger = getLogger(__name__)


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

    def __init__(self, *args, **kwargs):
        # TODO Support multiple concurrent requests
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

    def _should_stop(self):
        if self._finished:
            return True

        if self.request.connection and getattr(self.request.connection, 'stream', None):
            return self.request.connection.stream.closed()  # type: ignore

        return True

    def send_feed(self, camera: Camera):
        while not self._should_stop():
            frame = self._get_frame(camera, timeout=5.0)
            if frame:
                self.write(frame)
                self.flush()

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

    def get(self, plugin: str, route: str, extension: str = '') -> None:
        self._set_request_type_and_extension(route, extension)
        if not (self._request_type and self._extension):
            self.write_error(404, 'Not Found')
            return

        stream_class = StreamWriter.get_class_by_name(self._extension)
        camera = self._get_camera(plugin)
        self.set_header('Content-Type', stream_class.mimetype)

        with camera.open(
            stream=True,
            stream_format=self._extension,
            frames_dir=None,
            **self._get_args(self.request.arguments),
        ) as session:
            camera.start_camera(session)
            if self._request_type == RequestType.PHOTO:
                self.send_frame(session)
            elif self._request_type == RequestType.VIDEO:
                self.send_feed(session)

        self.finish()
