import threading

from typing import IO, Optional, List, Tuple, Union

from platypush.plugins import action
from platypush.plugins.camera import CameraPlugin, Camera
from platypush.utils import wait_for_either

from .model import PiCameraInfo, PiCamera


class CameraPiLegacyPlugin(CameraPlugin):
    """
    Plugin to interact with a `Pi Camera
    <https://www.raspberrypi.com/documentation/accessories/camera.html>`_.

    .. warning::
        This plugin is **DEPRECATED**, as it relies on the old ``picamera``
        module.


    The ``picamera`` module used in this plugin is deprecated and no longer
    maintained. The `picamera2 <https://github.com/raspberrypi/picamera2>`_
    module is advised instead, which is used by
    :class:`platypush.plugins.camera.pi.CameraPiPlugin`.

    You may want to use this plugin if you are running an old OS that does not
    support the new ``picamera2`` module. Even in that case, you may probably
    consider using :class:`platypush.plugins.camera.ffmpeg.FfmpegCameraPlugin`
    or :class:`platypush.plugins.camera.gstreamer.GStreamerCameraPlugin`, as
    ``picamera`` is not maintained anymore and may not work properly.
    """

    _camera_class = PiCamera
    _camera_info_class = PiCameraInfo
    _supported_encoders = ('h264', 'mjpeg')

    def __init__(
        self,
        device: int = 0,
        fps: float = 30.0,
        warmup_seconds: float = 2.0,
        sharpness: int = 0,
        contrast: int = 0,
        brightness: int = 50,
        video_stabilization: bool = False,
        iso: int = 0,
        exposure_compensation: int = 0,
        exposure_mode: str = 'auto',
        meter_mode: str = 'average',
        awb_mode: str = 'auto',
        image_effect: str = 'none',
        led_pin: Optional[int] = None,
        color_effects: Optional[Union[str, List[str]]] = None,
        zoom: Tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0),
        stream_format: str = 'h264',
        **camera,
    ):
        """
        :param device: Camera device number (default: 0). Only supported on
            devices with multiple camera slots.
        :param fps: Frames per second (default: 30.0).
        :param warmup_seconds: Seconds to wait for the camera to warm up
            before taking a photo (default: 2.0).
        :param sharpness: Sharpness level, as an integer between -100 and 100.
        :param contrast: Contrast level, as an integer between -100 and 100.
        :param brightness: Brightness level, as an integer between 0 and 100.
        :param video_stabilization: Enable video stabilization (default: False).
        :param iso: ISO level (default: 0).
        :param exposure_compensation: Exposure compensation level, as an
            integer between -25 and 25.
        :param exposure_mode: Exposure mode. Allowed values:

            - ``off``
            - ``auto`` (default)
            - ``night``
            - ``nightpreview``
            - ``backlight``
            - ``spotlight``
            - ``sports``
            - ``snow``
            - ``beach``
            - ``verylong``
            - ``fixedfps``
            - ``antishake``
            - ``fireworks``

        :param meter_mode: Metering mode used for the exposure. Allowed values:

            - ``average`` (default)
            - ``spot``
            - ``backlit``
            - ``matrix``

        :param awb_mode: Auto white balance mode. Allowed values:

            - ``off``
            - ``auto`` (default)
            - ``sunlight``
            - ``cloudy``
            - ``shade``
            - ``tungsten``
            - ``fluorescent``
            - ``incandescent``
            - ``flash``
            - ``horizon``

        :param image_effect: Image effect applied to the camera. Allowed values:

            - ``none`` (default)
            - ``negative``
            - ``solarize``
            - ``sketch``
            - ``denoise``
            - ``emboss``
            - ``oilpaint``
            - ``hatch``
            - ``gpen``
            - ``pastel``
            - ``watercolor``
            - ``film``
            - ``blur``
            - ``saturation``
            - ``colorswap``
            - ``washedout``
            - ``posterise``
            - ``colorpoint``
            - ``colorbalance``
            - ``cartoon``
            - ``deinterlace1``
            - ``deinterlace2``

        :param led_pin: LED PIN number, if the camera LED is wired to a GPIO
            PIN and you want to control it.
        :param zoom: Camera zoom, in the format ``(x, y, width, height)``
            (default: ``(0.0, 0.0, 1.0, 1.0)``).
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
        self.camera_info.video_stabilization = video_stabilization  # type: ignore
        self.camera_info.iso = iso  # type: ignore
        self.camera_info.exposure_compensation = exposure_compensation  # type: ignore
        self.camera_info.meter_mode = meter_mode  # type: ignore
        self.camera_info.exposure_mode = exposure_mode  # type: ignore
        self.camera_info.awb_mode = awb_mode  # type: ignore
        self.camera_info.image_effect = image_effect  # type: ignore
        self.camera_info.color_effects = color_effects  # type: ignore
        self.camera_info.zoom = zoom  # type: ignore
        self.camera_info.led_pin = led_pin  # type: ignore

    def prepare_device(self, device: Camera, **_):
        import picamera  # type: ignore

        assert isinstance(device, PiCamera), f'Invalid camera type: {type(device)}'
        camera = picamera.PiCamera(
            camera_num=device.info.device,
            resolution=device.info.resolution,
            framerate=device.info.fps,
            led_pin=device.info.led_pin,
        )

        camera.hflip = device.info.horizontal_flip
        camera.vflip = device.info.vertical_flip
        camera.sharpness = device.info.sharpness
        camera.contrast = device.info.contrast
        camera.brightness = device.info.brightness
        camera.video_stabilization = device.info.video_stabilization
        camera.iso = device.info.iso
        camera.exposure_compensation = device.info.exposure_compensation
        camera.exposure_mode = device.info.exposure_mode
        camera.meter_mode = device.info.meter_mode
        camera.awb_mode = device.info.awb_mode
        camera.image_effect = device.info.image_effect
        camera.color_effects = device.info.color_effects
        camera.rotation = device.info.rotate or 0
        camera.zoom = device.info.zoom

        return camera

    def release_device(self, device: Camera):
        import picamera  # type: ignore

        assert isinstance(device, PiCamera), f'Invalid camera type: {type(device)}'
        if device.object:
            try:
                device.object.stop_recording()
            except (ConnectionError, picamera.PiCameraNotRecording):
                pass

        if device.object and not device.object.closed:
            try:
                device.object.close()
            except (ConnectionError, picamera.PiCameraClosed):
                pass

    def capture_frame(self, device: Camera, *_, **__):
        import numpy as np
        from PIL import Image

        assert device.info.resolution, 'Invalid resolution'
        assert device.object, 'Camera not opened'
        shape = (
            device.info.resolution[1] + (device.info.resolution[1] % 16),
            device.info.resolution[0] + (device.info.resolution[0] % 32),
            3,
        )

        frame = np.empty(shape, dtype=np.uint8)
        device.object.capture(frame, 'rgb')
        return Image.fromarray(frame)

    def start_preview(self, camera: Camera):
        """
        Start camera preview.
        """
        assert camera.object, 'Camera not opened'
        camera.object.start_preview()

    def stop_preview(self, camera: Camera):
        """
        Stop camera preview.
        """
        if not camera.object:
            return

        try:
            camera.object.stop_preview()
        except Exception as e:
            self.logger.warning(str(e))

    @action
    def capture_preview(
        self,
        device: Optional[Union[str, int]] = None,
        duration: Optional[float] = None,
        n_frames: Optional[int] = None,
        **camera,
    ) -> dict:
        camera = self.open_device(device=device, **camera)
        self.start_preview(camera)

        if n_frames:
            duration = n_frames * (camera.info.fps or 0)
        if duration:
            threading.Timer(duration, lambda: self.stop_preview(camera))

        return self.status()  # type: ignore

    def _streaming_loop(self, camera: Camera, stream_format: str, sock: IO, *_, **__):
        from picamera import PiCamera as PiCamera_  # type: ignore

        stream_format = stream_format.lower()
        assert (
            stream_format in self._supported_encoders
        ), f'Invalid stream format: {stream_format}. Supported formats: {", ".join(self._supported_encoders)}'
        assert isinstance(camera, PiCamera), f'Invalid camera type: {type(camera)}'
        assert camera.object and isinstance(
            camera.object, PiCamera_
        ), f'Invalid camera object type: {type(camera.object)}'

        cam = camera.object
        try:
            cam.start_recording(sock, format=stream_format)
            while not wait_for_either(
                camera.stop_stream_event, self._should_stop, timeout=1
            ):
                cam.wait_recording(1)
        except ConnectionError:
            self.logger.info('Client closed connection')
        finally:
            try:
                cam.stop_recording()
                self.stop_streaming()
            except Exception as e:
                self.logger.warning('Could not stop streaming: %s', e)

    def _prepare_stream_writer(self, *_, **__):
        """
        Overrides the base method to do nothing - the stream writer is handled
        by the picamera library.
        """


# vim:sw=4:ts=4:et:
