from dataclasses import dataclass
from typing import Optional, Union, List, Tuple

from platypush.plugins.camera import CameraInfo, Camera


@dataclass
class PiCameraInfo(CameraInfo):
    sharpness: int = 0
    contrast: int = 0
    brightness: int = 50
    video_stabilization: bool = False
    iso: int = 0
    exposure_compensation: int = 0
    exposure_mode: str = 'auto'
    meter_mode: str = 'average'
    awb_mode: str = 'auto'
    image_effect: str = 'none'
    color_effects: Optional[Union[str, List[str]]] = None
    zoom: Tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0)
    led_pin: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            'sharpness': self.sharpness,
            'contrast': self.contrast,
            'brightness': self.brightness,
            'video_stabilization': self.video_stabilization,
            'iso': self.iso,
            'exposure_compensation': self.exposure_compensation,
            'exposure_mode': self.exposure_mode,
            'meter_mode': self.meter_mode,
            'awb_mode': self.awb_mode,
            'image_effect': self.image_effect,
            'color_effects': self.color_effects,
            'zoom': self.zoom,
            'led_pin': self.led_pin,
            **super().to_dict()
        }


class PiCamera(Camera):
    info: PiCameraInfo


# vim:sw=4:ts=4:et:
