from typing import Optional, Union

from platypush.plugins.camera import CameraPlugin, Camera
from platypush.plugins.camera.model.writer.cv import CvFileWriter


class CameraCvPlugin(CameraPlugin):
    """
    Plugin to control generic cameras over OpenCV.

    Requires:

        * **opencv** (``pip install opencv-python``)
        * **Pillow** (``pip install Pillow``)

    """

    def __init__(self, color_transform: Optional[str] = 'COLOR_BGR2RGB', video_type: str = 'XVID',
                 video_writer: str = 'ffmpeg', **kwargs):
        """
        :param device: Device ID (0 for the first camera, 1 for the second etc.) or path (e.g. ``/dev/video0``).
        :param video_type: Default video type to use when exporting captured frames to camera (default: 0, infers the
            type from the video file extension). See
            `here <https://docs.opencv.org/4.0.1/dd/d9e/classcv_1_1VideoWriter.html#afec93f94dc6c0b3e28f4dd153bc5a7f0>`_
            for a reference on the supported types (e.g. 'MJPEG', 'XVID', 'H264', 'X264', 'AVC1' etc.)

        :param color_transform: Color transformation to apply to the captured frames. See
            https://docs.opencv.org/3.2.0/d7/d1b/group__imgproc__misc.html for a full list of supported color
            transformations (default: "``COLOR_RGB2BGR``")

        :param video_writer: Class to be used to write frames to a video file. Supported values:

                - ``ffmpeg``: Use the FFmpeg writer (default, and usually more reliable - it requires ``ffmpeg``
                    installed).
                - ``cv``: Use the native OpenCV writer.

            The FFmpeg video writer requires ``scikit-video`` (``pip install scikit-video``) and ``ffmpeg``.

        :param kwargs: Extra arguments to be passed up to :class:`platypush.plugins.camera.CameraPlugin`.
        """
        super().__init__(color_transform=color_transform, video_type=video_type, **kwargs)
        if video_writer == 'cv':
            self._video_writer_class = CvFileWriter

    def prepare_device(self, device: Camera):
        import cv2

        cam = cv2.VideoCapture(device.info.device)
        if device.info.resolution and device.info.resolution[0]:
            cam.set(cv2.CAP_PROP_FRAME_WIDTH, device.info.resolution[0])
            cam.set(cv2.CAP_PROP_FRAME_HEIGHT, device.info.resolution[1])

        return cam

    def release_device(self, device: Camera):
        if device.object:
            device.object.release()
            device.object = None

    def capture_frame(self, camera: Camera, *args, **kwargs):
        import cv2
        from PIL import Image
        ret, frame = camera.object.read()
        assert ret, 'Cannot retrieve frame from {}'.format(camera.info.device)

        color_transform = camera.info.color_transform
        if isinstance(color_transform, str):
            color_transform = getattr(cv2, color_transform or self.camera_info.color_transform)
        if color_transform:
            frame = cv2.cvtColor(frame, color_transform)

        return Image.fromarray(frame)

    @staticmethod
    def transform_frame(frame, color_transform: Union[str, int]):
        return frame


# vim:sw=4:ts=4:et:
