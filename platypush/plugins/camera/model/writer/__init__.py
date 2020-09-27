import io
import logging
import os
import threading
import time

from abc import ABC, abstractmethod
from typing import Optional, IO

from PIL.Image import Image


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
    def write(self, img: Image):
        """
        Write an image to the channel.

        :param img: PIL Image instance.
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

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager-based interface.
        """
        self.close()


class FileVideoWriter(VideoWriter, ABC):
    """
    Abstract class to handle frames-to-video file operations.
    """
    def __init__(self, *args, output_file: str, **kwargs):
        VideoWriter.__init__(self, *args, **kwargs)
        self.output_file = os.path.abspath(os.path.expanduser(output_file))


class StreamWriter(VideoWriter, ABC):
    """
    Abstract class for camera streaming operations.
    """
    def __init__(self, *args, sock: Optional[IO] = None, **kwargs):
        VideoWriter.__init__(self, *args, **kwargs)
        self.frame: Optional[bytes] = None
        self.frame_time: Optional[float] = None
        self.buffer = io.BytesIO()
        self.ready = threading.Condition()
        self.sock = sock

    def write(self, image: Image):
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

    @abstractmethod
    def encode(self, image: Image) -> bytes:
        """
        Encode an image before sending it to the channel.

        :param image: PIL Image object.
        :return: The bytes-encoded representation of the frame.
        """
        raise NotImplementedError()

    def close(self):
        self.buffer.close()
        if self.sock:
            # noinspection PyBroadException
            try:
                self.sock.close()
            except:
                pass

        super().close()

    @staticmethod
    def get_class_by_name(name: str):
        from platypush.plugins.camera.model.writer.index import StreamHandlers
        name = name.upper()
        assert hasattr(StreamHandlers, name), 'No such stream handler: {}. Supported types: {}'.format(
            name, [hndl.name for hndl in list(StreamHandlers)])

        return getattr(StreamHandlers, name).value


# vim:sw=4:ts=4:et:
