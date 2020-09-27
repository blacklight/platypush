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
    bind_address: Optional[str] = None
    capture_timeout: float = 20.0
    color_transform: Optional[str] = None
    ffmpeg_bin: Optional[str] = None
    fps: Optional[float] = None
    frames_dir: Optional[str] = None
    grayscale: Optional[bool] = None
    horizontal_flip: bool = False
    input_codec: Optional[str] = None
    input_format: Optional[str] = None
    listen_port: Optional[int] = None
    output_codec: Optional[str] = None
    output_format: Optional[str] = None
    resolution: Optional[Tuple[int, int]] = None
    rotate: Optional[float] = None
    scale_x: Optional[float] = None
    scale_y: Optional[float] = None
    stream_format: Optional[str] = None
    vertical_flip: bool = False
    warmup_frames: int = 0
    warmup_seconds: float = 0.

    def set(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def to_dict(self) -> dict:
        return {
            'bind_address': self.bind_address,
            'capture_timeout': self.capture_timeout,
            'color_transform': self.color_transform,
            'device': self.device,
            'ffmpeg_bin': self.ffmpeg_bin,
            'fps': self.fps,
            'frames_dir': self.frames_dir,
            'grayscale': self.grayscale,
            'horizontal_flip': self.horizontal_flip,
            'input_codec': self.input_codec,
            'input_format': self.input_format,
            'listen_port': self.listen_port,
            'output_codec': self.output_codec,
            'output_format': self.output_format,
            'resolution': list(self.resolution or ()),
            'rotate': self.rotate,
            'scale_x': self.scale_x,
            'scale_y': self.scale_y,
            'stream_format': self.stream_format,
            'vertical_flip': self.vertical_flip,
            'warmup_frames': self.warmup_frames,
            'warmup_seconds': self.warmup_seconds,
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
