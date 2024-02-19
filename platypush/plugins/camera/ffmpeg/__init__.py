import signal
import subprocess
from typing import Iterable, Optional

from PIL import Image
from PIL.Image import Image as ImageType

from platypush.plugins.camera import CameraPlugin
from platypush.plugins.camera.ffmpeg.model import FFmpegCamera, FFmpegCameraInfo
from platypush.plugins.camera.model.camera import Camera


class CameraFfmpegPlugin(CameraPlugin):
    """
    Plugin to interact with a camera over FFmpeg.
    """

    _camera_class = FFmpegCamera
    _camera_info_class = FFmpegCameraInfo

    def __init__(
        self,
        device: Optional[str] = '/dev/video0',
        input_format: str = 'v4l2',
        ffmpeg_args: Iterable[str] = (),
        **opts,
    ):
        """
        :param device: Path to the camera device (default: ``/dev/video0``).
        :param input_format: FFmpeg input format for the camera device (default: ``v4l2``).
        :param ffmpeg_args: Extra options to be passed to the FFmpeg executable.
        :param opts: Camera options - see constructor of :class:`platypush.plugins.camera.CameraPlugin`.
        """
        super().__init__(device=device, input_format=input_format, **opts)
        self.camera_info.ffmpeg_args = ffmpeg_args or ()  # type: ignore

    def prepare_device(self, device: Camera, **_) -> subprocess.Popen:
        assert isinstance(device, FFmpegCamera)
        warmup_seconds = self._get_warmup_seconds(device)
        ffmpeg = [
            device.info.ffmpeg_bin,
            '-y',
            '-f',
            device.info.input_format,
            '-i',
            device.info.device,
            '-s',
            *(
                (f'{device.info.resolution[0]}x{device.info.resolution[1]}',)
                if device.info.resolution
                else ()
            ),
            '-ss',
            str(warmup_seconds),
            *(('-r', str(device.info.fps)) if device.info.fps else ()),
            '-pix_fmt',
            'rgb24',
            '-f',
            'rawvideo',
            *device.info.ffmpeg_args,
            '-',
        ]

        self.logger.info('Running FFmpeg command: "%s"', ' '.join(ffmpeg))
        proc = subprocess.Popen(ffmpeg, stdout=subprocess.PIPE)
        # Start in suspended mode
        proc.send_signal(signal.SIGSTOP)
        return proc

    def start_camera(self, camera: Camera, *args, preview: bool = False, **kwargs):
        assert isinstance(camera, FFmpegCamera)
        super().start_camera(*args, camera=camera, preview=preview, **kwargs)
        if camera.object:
            camera.object.send_signal(signal.SIGCONT)

    def release_device(self, device: Camera):
        assert isinstance(device, FFmpegCamera)
        if device.object:
            device.object.terminate()
            if device.object.stdout:
                device.object.stdout.close()
            device.object = None  # type: ignore

    def wait_capture(self, camera: Camera):
        assert isinstance(camera, FFmpegCamera)
        if camera.object and camera.object.poll() is None:
            try:
                camera.object.wait(timeout=camera.info.capture_timeout)
            except Exception as e:
                self.logger.warning('Error on FFmpeg capture wait: %s', e)

    def capture_frame(self, device: Camera, *_, **__) -> Optional[ImageType]:
        assert isinstance(device, FFmpegCamera)
        assert device.info.resolution, 'Resolution not set'
        assert device.object.stdout, 'Camera not started'

        raw_size = device.info.resolution[0] * device.info.resolution[1] * 3
        data = device.object.stdout.read(raw_size)
        if len(data) < raw_size:
            return
        return Image.frombytes('RGB', device.info.resolution, data)


# vim:sw=4:ts=4:et:
