import math
import threading
from dataclasses import dataclass
from typing import Optional, Union, Tuple, Set

import numpy as np

from platypush.plugins.camera.model.writer import StreamWriter, VideoWriter, FileVideoWriter
from platypush.plugins.camera.model.writer.preview import PreviewWriter


@dataclass
class CameraInfo:
    device: Optional[Union[int, str]]
    resolution: Optional[Tuple[int, int]] = None
    color_transform: Optional[str] = None
    frames_dir: Optional[str] = None
    rotate: Optional[float] = None
    horizontal_flip: bool = False
    vertical_flip: bool = False
    scale_x: Optional[float] = None
    scale_y: Optional[float] = None
    warmup_frames: int = 0
    warmup_seconds: float = 0.
    capture_timeout: float = 20.0
    fps: Optional[float] = None
    grayscale: Optional[bool] = None
    video_type: Optional[str] = None
    stream_format: str = 'mjpeg'
    listen_port: Optional[int] = None
    bind_address: Optional[str] = None

    def set(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_dict(self) -> dict:
        return {
            'device': self.device,
            'color_transform': self.color_transform,
            'frames_dir': self.frames_dir,
            'rotate': self.rotate,
            'horizontal_flip': self.horizontal_flip,
            'vertical_flip': self.vertical_flip,
            'scale_x': self.scale_x,
            'scale_y': self.scale_y,
            'warmup_frames': self.warmup_frames,
            'warmup_seconds': self.warmup_seconds,
            'capture_timeout': self.capture_timeout,
            'fps': self.fps,
            'grayscale': self.grayscale,
            'resolution': list(self.resolution or ()),
            'video_type': self.video_type,
            'stream_format': self.stream_format,
            'listen_port': self.listen_port,
            'bind_address': self.bind_address,
        }

    def clone(self):
        # noinspection PyArgumentList
        return self.__class__(**self.to_dict())


@dataclass
class Camera:
    info: CameraInfo
    start_event: threading.Event = threading.Event()
    stream_event: threading.Event = threading.Event()
    capture_thread: Optional[threading.Thread] = None
    stream_thread: Optional[threading.Thread] = None
    object = None
    stream: Optional[StreamWriter] = None
    preview: Optional[PreviewWriter] = None
    file_writer: Optional[FileVideoWriter] = None

    def get_outputs(self) -> Set[VideoWriter]:
        writers = set()
        # if self.preview and self.preview.is_alive():
        if self.preview and not self.preview.closed:
            writers.add(self.preview)

        if self.stream and not self.stream.closed:
            writers.add(self.stream)

        if self.file_writer and not self.file_writer.closed:
            writers.add(self.file_writer)

        return writers

    def effective_resolution(self) -> Tuple[int, int]:
        rot = (self.info.rotate or 0) * math.pi / 180
        sin = math.sin(rot)
        cos = math.cos(rot)
        scale = np.array([[self.info.scale_x or 1., self.info.scale_y or 1.]])
        resolution = np.array([[self.info.resolution[0], self.info.resolution[1]]])
        rot_matrix = np.array([[sin, cos], [cos, sin]])
        resolution = (scale * abs(np.cross(rot_matrix, resolution)))[0]
        return int(round(resolution[0])), int(round(resolution[1]))


# vim:sw=4:ts=4:et:
