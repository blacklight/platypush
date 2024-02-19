import os
import time

from typing import Optional, Union

from platypush.plugins import action
from platypush.plugins.camera import CameraPlugin, Camera

from .model import PiCameraInfo, PiCamera


class CameraPiPlugin(CameraPlugin):
    """
    Plugin to interact with a `Pi Camera
    <https://www.raspberrypi.com/documentation/accessories/camera.html>`_.

    This integration is intended to work with the `picamera2
    <https://github.com/raspberrypi/picamera2>`_ module.

    If you are running a very old OS that only provides the deprecated
    `picamera <https://github.com/waveform80/picamera>`_ module, or you rely on
    features that are currently only supported by the old module, you should
    use :class:`platypush.plugins.camera.pi_legacy.CameraPiLegacyPlugin`
    instead.
    """

    _camera_class = PiCamera
    _camera_info_class = PiCameraInfo

    _awb_modes = [
        "Auto",
        "Incandescent",
        "Tungsten",
        "Fluorescent",
        "Indoor",
        "Daylight",
        "Cloudy",
    ]

    def __init__(
        self,
        device: int = 0,
        fps: float = 30.0,
        warmup_seconds: float = 2.0,
        sharpness: float = 1.0,
        contrast: float = 1.0,
        brightness: float = 0.0,
        iso: int = 0,
        exposure_compensation: float = 0.0,
        awb_mode: str = 'Auto',
        **camera,
    ):
        """
        :param device: Camera device number (default: 0). Only supported on
            devices with multiple camera slots.
        :param fps: Frames per second (default: 30.0).
        :param warmup_seconds: Seconds to wait for the camera to warm up
            before taking a photo (default: 2.0).
        :param sharpness: Sharpness level, as a float between 0.0 and 16.0,
            where 1.0 is the default value, and higher values are mapped to
            higher sharpness levels.
        :param contrast: Contrast level, as a float between 0.0 and 32.0, where
            1.0 is the default value, and higher values are mapped to higher
            contrast levels.
        :param brightness: Brightness level, as a float between -1.0 and 1.0.
        :param video_stabilization: Enable video stabilization (default: False).
            Only available on the old picamera module for now.
        :param iso: ISO level (default: 0).
        :param exposure_compensation: Exposure compensation level, as a float
            between -8.0 and 8.0.
        :param awb_mode: Auto white balance mode. Allowed values:

            - ``Auto`` (default)
            - ``Daylight``
            - ``Cloudy``
            - ``Indoor``
            - ``Fluorescent``

        :param camera: Options for the base camera plugin (see
            :class:`platypush.plugins.camera.CameraPlugin`).
        """
        super().__init__(
            device=device, fps=fps, warmup_seconds=warmup_seconds, **camera
        )

        self.camera_info.sharpness = sharpness  # type: ignore
        self.camera_info.contrast = contrast  # type: ignore
        self.camera_info.brightness = brightness  # type: ignore
        self.camera_info.iso = iso  # type: ignore
        self.camera_info.exposure_compensation = exposure_compensation  # type: ignore
        self.camera_info.awb_mode = awb_mode  # type: ignore

    def prepare_device(
        self, device: Camera, start: bool = True, video: bool = False, **_
    ):
        from libcamera import Transform  # type: ignore
        from picamera2 import Picamera2  # type: ignore

        assert isinstance(device, PiCamera), f'Invalid device type: {type(device)}'
        camera = Picamera2(camera_num=device.info.device)
        cfg_params = {
            'main': {
                'format': 'XBGR8888' if video else 'BGR888',
                **(
                    {'size': tuple(map(int, device.info.resolution))}
                    if device.info.resolution
                    else {}
                ),
            },
            **(
                {
                    'transform': Transform(
                        # It may seem counterintuitive, but the picamera2 library's flip
                        # definition is the opposite of ours
                        hflip=device.info.vertical_flip,
                        vflip=device.info.horizontal_flip,
                    ),
                }
                if video
                # We don't need to flip the image for individual frames, the base camera
                # class methods will take care of that
                else {}
            ),
            'controls': {
                'Brightness': float(device.info.brightness),
                'Contrast': float(device.info.contrast),
                'Sharpness': float(device.info.sharpness),
                'AwbMode': self._awb_modes.index(device.info.awb_mode),
            },
        }

        cfg = (
            camera.create_video_configuration
            if video
            else camera.create_still_configuration
        )(**cfg_params)

        camera.configure(cfg)
        if start:
            camera.start()
            time.sleep(max(1, device.info.warmup_seconds))

        return camera

    def release_device(self, device: Camera):
        if device.object:
            device.object.stop()
            device.object.close()

    def capture_frame(self, device: Camera, *_, **__):
        assert device.object, 'Camera not open'
        return device.object.capture_image('main')

    @action
    def capture_video(
        self,
        device: Optional[int] = None,
        duration: Optional[float] = None,
        video_file: Optional[str] = None,
        preview: bool = False,
        **camera,
    ) -> Optional[Union[str, dict]]:
        """
        Capture a video.

        :param device: 0-based index of the camera to capture from, if the
            device supports multiple cameras. Default: use the configured
            camera index or the first available camera.
        :param duration: Record duration in seconds (default: None, record
            until :meth:`.stop_capture``).
        :param video_file: If set, the stream will be recorded to the specified
            video file (default: None).
        :param camera: Camera parameters override - see constructors parameters.
        :param preview: Show a preview of the camera frames.
        :return: If duration is specified, the method will wait until the
            recording is done and return the local path to the recorded
            resource. Otherwise, it will return the status of the camera device
            after starting it.
        """
        from picamera2 import Picamera2  # type: ignore
        from picamera2.encoders import H264Encoder  # type: ignore

        assert video_file, 'Video file is required'
        camera = self.open_device(
            device=device, ctx={'start': False, 'video': True}, **camera
        )

        encoder = H264Encoder()
        assert camera.object, 'Camera not open'
        assert isinstance(
            camera.object, Picamera2
        ), f'Invalid camera object type: {type(camera.object)}'

        if preview:
            camera.object.start_preview()

        # Only H264 is supported for now
        camera.object.start_recording(encoder, os.path.expanduser(video_file))

        if duration:
            self.wait_stop(duration)
            try:
                if preview:
                    camera.object.stop_preview()
            finally:
                if camera.object:
                    camera.object.stop_recording()
                    camera.object.close()

            return video_file

        return self.status(camera.info.device).output

    @action
    def start_streaming(
        self, duration: Optional[float] = None, stream_format: str = 'h264', **camera
    ) -> dict:
        camera = self.open_device(stream_format=stream_format, **camera)
        return self._start_streaming(camera, duration, stream_format)  # type: ignore


# vim:sw=4:ts=4:et:
