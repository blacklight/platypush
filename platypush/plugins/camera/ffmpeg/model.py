from dataclasses import dataclass
from subprocess import Popen
from typing import Tuple

from platypush.plugins.camera import CameraInfo, Camera


@dataclass
class FFmpegCameraInfo(CameraInfo):
    ffmpeg_args: Tuple[str] = ()

    def to_dict(self) -> dict:
        return {
            'ffmpeg_args': list(self.ffmpeg_args or ()),
            **super().to_dict()
        }


class FFmpegCamera(Camera):
    info: FFmpegCameraInfo
    object: Popen


# vim:sw=4:ts=4:et:
