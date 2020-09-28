import signal
import subprocess
from typing import Optional, Tuple

from PIL import Image
from PIL.Image import Image as ImageType

from platypush.plugins.camera import CameraPlugin
from platypush.plugins.camera.ffmpeg.model import FFmpegCamera, FFmpegCameraInfo


class CameraFfmpegPlugin(CameraPlugin):
    """
    Plugin to interact with a camera over FFmpeg.

    Requires:

        * **ffmpeg** package installed on the system.

    """

    _camera_class = FFmpegCamera
    _camera_info_class = FFmpegCameraInfo

    def __init__(self, device: Optional[str] = '/dev/video0', input_format: str = 'v4l2', ffmpeg_args: Tuple[str] = (),
                 **opts):
        """
        :param device: Path to the camera device (default: ``/dev/video0``).
        :param input_format: FFmpeg input format for the the camera device (default: ``v4l2``).
        :param ffmpeg_args: Extra options to be passed to the FFmpeg executable.
        :param opts: Camera options - see constructor of :class:`platypush.plugins.camera.CameraPlugin`.
        """
        super().__init__(device=device, input_format=input_format, **opts)
        self.camera_info.ffmpeg_args = ffmpeg_args or ()

    def prepare_device(self, camera: FFmpegCamera) -> subprocess.Popen:
        warmup_seconds = self._get_warmup_seconds(camera)
        ffmpeg = [camera.info.ffmpeg_bin, '-y', '-f', camera.info.input_format, '-i', camera.info.device, '-s',
                  '{}x{}'.format(*camera.info.resolution), '-ss', str(warmup_seconds),
                  *(('-r', str(camera.info.fps)) if camera.info.fps else ()),
                  '-pix_fmt', 'rgb24', '-f', 'rawvideo', *camera.info.ffmpeg_args, '-']

        self.logger.info('Running FFmpeg: {}'.format(' '.join(ffmpeg)))
        proc = subprocess.Popen(ffmpeg, stdout=subprocess.PIPE)
        # Start in suspended mode
        proc.send_signal(signal.SIGSTOP)
        return proc

    def start_camera(self, camera: FFmpegCamera, preview: bool = False, *args, **kwargs):
        super().start_camera(*args, camera=camera, preview=preview, **kwargs)
        if camera.object:
            camera.object.send_signal(signal.SIGCONT)

    def release_device(self, camera: FFmpegCamera):
        if camera.object:
            camera.object.terminate()
            if camera.object.stdout:
                camera.object.stdout.close()
            camera.object = None

    def wait_capture(self, camera: FFmpegCamera) -> None:
        if camera.object and camera.object.poll() is None:
            try:
                camera.object.wait(timeout=camera.info.capture_timeout)
            except Exception as e:
                self.logger.warning('Error on FFmpeg capture wait: {}'.format(str(e)))

    def capture_frame(self, camera: FFmpegCamera, *args, **kwargs) -> Optional[ImageType]:
        raw_size = camera.info.resolution[0] * camera.info.resolution[1] * 3
        data = camera.object.stdout.read(raw_size)
        if len(data) < raw_size:
            return
        return Image.frombytes('RGB', camera.info.resolution, data)


# vim:sw=4:ts=4:et:
