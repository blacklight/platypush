from typing import Optional

from PIL import Image
from PIL.Image import Image as ImageType

from platypush.plugins.camera import CameraPlugin
from platypush.plugins.camera.gstreamer.model import GStreamerCamera
from platypush.common.gstreamer import Pipeline


class CameraGstreamerPlugin(CameraPlugin):
    """
    Plugin to interact with a camera over GStreamer.

    Requires:

        * **gst-python**
        * **pygobject**

    On Debian and derived systems:

        * ``[sudo] apt-get install python3-gi python3-gst-1.0``

    On Arch and derived systems:

        * ``[sudo] pacman -S gst-python``

    """

    _camera_class = GStreamerCamera

    def __init__(self, device: Optional[str] = '/dev/video0', **opts):
        """
        :param device: Path to the camera device (default ``/dev/video0``).
        :param opts: Camera options - see constructor of :class:`platypush.plugins.camera.CameraPlugin`.
        """
        super().__init__(device=device, **opts)

    def prepare_device(self, camera: GStreamerCamera) -> Pipeline:
        pipeline = Pipeline()
        src = pipeline.add_source('v4l2src', device=camera.info.device)
        convert = pipeline.add('videoconvert')
        assert camera.info and camera.info.resolution

        video_filter = pipeline.add(
            'capsfilter',
            caps='video/x-raw,format=RGB,width={width},height={height},framerate={fps}/1'.format(
                width=camera.info.resolution[0],
                height=camera.info.resolution[1],
                fps=camera.info.fps,
            ),
        )

        sink = pipeline.add_sink('appsink', name='appsink', sync=False)
        pipeline.link(src, convert, video_filter, sink)
        return pipeline

    def start_camera(
        self, camera: GStreamerCamera, preview: bool = False, *args, **kwargs
    ):
        super().start_camera(*args, camera=camera, preview=preview, **kwargs)
        if camera.object:
            camera.object.play()

    def release_device(self, camera: GStreamerCamera):
        if camera.object:
            camera.object.stop()

    def capture_frame(self, camera: GStreamerCamera, *_, **__) -> Optional[ImageType]:
        if not (camera.info and camera.info.fps and camera.info.resolution):
            return None

        timed_out = not camera.object.data_ready.wait(
            timeout=5 + (1.0 / camera.info.fps)
        )
        if timed_out:
            self.logger.warning('Frame capture timeout')
            return None

        data = camera.object.data
        if data is None:
            return None

        camera.object.data_ready.clear()
        if (
            not data
            and len(data) != camera.info.resolution[0] * camera.info.resolution[1] * 3
        ):
            return None

        return Image.frombytes('RGB', camera.info.resolution, data)


# vim:sw=4:ts=4:et:
