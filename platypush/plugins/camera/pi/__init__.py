import os
import time
from typing import IO, Optional, Union

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
    use :class:`platypush.plugins.camera.pi.legacy.CameraPiLegacyPlugin`
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
        stream_format: str = 'h264',
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
        :param iso: ISO level (default: 0).
        :param exposure_compensation: Exposure compensation level, as a float
            between -8.0 and 8.0.
        :param awb_mode: Auto white balance mode. Allowed values:

            - ``Auto`` (default)
            - ``Daylight``
            - ``Cloudy``
            - ``Indoor``
            - ``Fluorescent``

        :param stream_format: Default format for the output when streamed to a
            network device. Available:

                - ``h264`` (default)
                - ``mjpeg``

        :param camera: Options for the base camera plugin (see
            :class:`platypush.plugins.camera.CameraPlugin`).
        """
        super().__init__(
            device=device,
            fps=fps,
            warmup_seconds=warmup_seconds,
            stream_format=stream_format,
            **camera,
        )

        self.camera_info.sharpness = sharpness  # type: ignore
        self.camera_info.contrast = contrast  # type: ignore
        self.camera_info.brightness = brightness  # type: ignore
        self.camera_info.iso = iso  # type: ignore
        self.camera_info.exposure_compensation = exposure_compensation  # type: ignore
        self.camera_info.awb_mode = awb_mode  # type: ignore

    def _get_transform(self, device: Camera):
        from libcamera import Orientation, Transform  # type: ignore
        from picamera2.utils import orientation_to_transform  # type: ignore

        rot = device.info.rotate
        if not rot:
            return Transform(
                # It may seem counterintuitive, but the picamera2 library's flip
                # definition is the opposite of ours
                hflip=device.info.vertical_flip,
                vflip=device.info.horizontal_flip,
            )

        if rot == 90:
            orient = (
                Orientation.Rotate90Mirror
                if device.info.vertical_flip
                else Orientation.Rotate90
            )
        elif rot == 180:
            orient = (
                Orientation.Rotate180Mirror
                if device.info.horizontal_flip
                else Orientation.Rotate180
            )
        elif rot == 270:
            orient = (
                Orientation.Rotate270Mirror
                if device.info.vertical_flip
                else Orientation.Rotate270
            )
        else:
            raise AssertionError(
                f'Invalid rotation: {rot}. Supported values: 0, 90, 180, 270'
            )

        return orientation_to_transform(orient)

    def prepare_device(
        self,
        device: Camera,
        start: bool = True,
        video: bool = False,
        stream: bool = False,
        **_,
    ):
        from picamera2 import Picamera2  # type: ignore

        assert isinstance(device, PiCamera), f'Invalid device type: {type(device)}'
        camera = Picamera2(camera_num=device.info.device)
        still = not (video or stream)
        cfg_params = {
            'main': {
                'format': 'XBGR8888' if not still else 'BGR888',
                **(
                    {'size': tuple(map(int, device.info.resolution))}
                    if device.info.resolution
                    else {}
                ),
            },
            **(
                {'transform': self._get_transform(device)}
                if not still
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
            if not still
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

    @property
    def _video_encoders_by_format(self) -> dict:
        from picamera2.encoders import H264Encoder, MJPEGEncoder  # type: ignore

        return {
            'h264': H264Encoder,
            'mjpeg': MJPEGEncoder,
        }

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

    def _streaming_loop(self, camera: Camera, stream_format: str, sock: IO, *_, **__):
        from picamera2 import Picamera2  # type: ignore
        from picamera2.outputs import FileOutput  # type: ignore

        encoder_cls = self._video_encoders_by_format.get(stream_format.lower())
        assert (
            encoder_cls
        ), f'Invalid stream format: {stream_format}. Supported formats: {", ".join(self._video_encoders_by_format)}'
        assert isinstance(camera, PiCamera), f'Invalid camera type: {type(camera)}'
        assert camera.object and isinstance(
            camera.object, Picamera2
        ), f'Invalid camera object type: {type(camera.object)}'

        cam = camera.object
        encoder = encoder_cls()
        cam.encoders = encoder
        encoder.output = FileOutput(sock)
        cam.start_encoder(encoder)
        cam.start()

    def _prepare_stream_writer(self, *_, **__):
        """
        Overrides the base method to do nothing - the stream writer is handled
        by the picamera2 library.
        """

    def _cleanup_stream(self, camera: Camera, *_, **__):
        cam = camera.object
        if not cam:
            return

        cam.stop()
        cam.stop_encoder()
        cam.close()


# vim:sw=4:ts=4:et:
