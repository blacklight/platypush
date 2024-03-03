from dataclasses import asdict, dataclass

from platypush.plugins.camera import CameraInfo, Camera


@dataclass
class PiCameraInfo(CameraInfo):
    """
    PiCamera info dataclass.
    """

    sharpness: int = 0
    contrast: int = 0
    brightness: int = 50
    video_stabilization: bool = False
    iso: int = 0
    exposure_compensation: int = 0
    hdr_mode: str = 'auto'
    meter_mode: str = 'average'
    awb_mode: str = 'auto'

    def to_dict(self) -> dict:
        return asdict(self)


class PiCamera(Camera):
    """
    PiCamera model.
    """

    info: PiCameraInfo  # type: ignore


# vim:sw=4:ts=4:et:
