import io
import logging
import multiprocessing
import os
import time

from abc import ABC, abstractmethod
from typing import Optional, IO

from platypush.utils import get_redis


class VideoWriter(ABC):
    """
    Generic class interface for handling frames-to-video operations.
    """

    mimetype: Optional[str] = None

    def __init__(self, camera, plugin, *_, **__):
        from platypush.plugins.camera import Camera, CameraPlugin

        self.logger = logging.getLogger(self.__class__.__name__)
        self.camera: Camera = camera
        self.plugin: CameraPlugin = plugin
        self.closed = False

    @abstractmethod
    def write(self, image):
        """
        Write an image to the channel.

        :param image: PIL Image instance.
        :type image: PIL.Image.Image
        """
        raise NotImplementedError()

    @abstractmethod
    def close(self):
        """
        Close the channel.
        """
        if self.camera:
            self.plugin.close_device(self.camera)
        self.closed = True

    def __enter__(self):
        """
        Context manager-based interface.
        """
        return self

    def __exit__(self, *_, **__):
        """
        Context manager-based interface.
        """
        self.close()


class FileVideoWriter(VideoWriter, ABC):
    """
    Abstract class to handle frames-to-video file operations.
    """

    def __init__(self, *args, output_file: str, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.output_file = os.path.abspath(os.path.expanduser(output_file))


class StreamWriter(VideoWriter, ABC):
    """
    Abstract class for camera streaming operations.
    """

    def __init__(
        self,
        *args,
        sock: Optional[IO] = None,
        redis_queue: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.frame: Optional[bytes] = None
        self.frame_time: Optional[float] = None
        self.buffer = io.BytesIO()
        self.ready = multiprocessing.Condition()
        self.redis_queue = redis_queue
        self.sock = sock

    def write(self, image):
        data = self.encode(image)
        with self.ready:
            if self.buffer.closed:
                return

            self.buffer.truncate()
            self.frame = self.buffer.getvalue()
            self.frame_time = time.time()
            self.ready.notify_all()

        self._sock_send(self.frame)
        if not self.buffer.closed:
            self.buffer.seek(0)
            return self.buffer.write(data)

    def _sock_send(self, data):
        if self.sock and data:
            try:
                self.sock.write(data)
            except ConnectionError:
                self.logger.info('Client connection closed')
                self.close()

        if self.redis_queue:
            get_redis().publish(self.redis_queue, data)

    @abstractmethod
    def encode(self, image) -> bytes:
        """
        Encode an image before sending it to the channel.

        :param image: PIL Image object.
        :return: The bytes-encoded representation of the frame.
        """
        raise NotImplementedError()

    def close(self):
        self.buffer.close()
        if self.sock:
            try:
                self.sock.close()
            except Exception as e:
                self.logger.warning('Could not close camera resource: %s', e)

        super().close()

    @staticmethod
    def get_class_by_name(name: str):
        from platypush.plugins.camera.model.writer.index import StreamHandlers

        name = name.upper()
        assert hasattr(
            StreamHandlers, name
        ), f'No such stream handler: {name}. Supported types: ' + (
            ', '.join([hndl.name for hndl in list(StreamHandlers)])
        )

        return getattr(StreamHandlers, name).value


# vim:sw=4:ts=4:et:
