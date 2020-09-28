import io
import os
import pathlib
import socket
import threading
import time

from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime
from multiprocessing import Process
from queue import Queue
from typing import Optional, Union, Dict, Tuple, IO

from platypush.config import Config
from platypush.message.event.camera import CameraRecordingStartedEvent, CameraPictureTakenEvent, \
    CameraRecordingStoppedEvent, CameraVideoRenderedEvent
from platypush.plugins import Plugin, action
from platypush.plugins.camera.model.camera import CameraInfo, Camera
from platypush.plugins.camera.model.exceptions import CameraException, CaptureAlreadyRunningException
from platypush.plugins.camera.model.writer import VideoWriter, StreamWriter
from platypush.plugins.camera.model.writer.ffmpeg import FFmpegFileWriter
from platypush.plugins.camera.model.writer.preview import PreviewWriter, PreviewWriterFactory
from platypush.utils import get_plugin_name_by_class

__all__ = ['Camera', 'CameraInfo', 'CameraException', 'CameraPlugin', 'CaptureAlreadyRunningException',
           'StreamWriter']


class CameraPlugin(Plugin, ABC):
    """
    Abstract plugin to control camera devices.

    If the :class:`platypush.backend.http.HttpBackend` is enabled then the plugins that implement this class can
    expose two endpoints:

        - ``http://host:8008/camera/<plugin>/photo<.extension>`` to capture a photo from the camera, where
            ``.extension`` can be ``.jpg``, ``.png`` or ``.bmp``.
        - ``http://host:8008/camera/<plugin>/video<.extension>`` to get a live feed from the camera, where
            ``.extension`` can be ``.mjpeg``, ``.mkv``/``.webm``, ``.mp4``/``.h264`` or ``.h265``.

    Both the endpoints support the same parameters of the constructor of this class (e.g. ``device``, ``warmup_frames``,
    ``duration`` etc.) as ``GET`` parameters.

    Requires:

        * **Pillow** (``pip install Pillow``) [optional] default handler for image transformations.
        * **wxPython** (``pip install wxPython``) [optional] default handler for camera previews (``ffplay`` will be
            used as a fallback if ``wxPython`` is not installed).
        * **ffmpeg** (see installation instructions for your OS) for rendering/streaming videos.

    Triggers:

        * :class:`platypush.message.event.camera.CameraRecordingStartedEvent`
            when a new video recording/photo burst starts
        * :class:`platypush.message.event.camera.CameraRecordingStoppedEvent`
            when a video recording/photo burst ends
        * :class:`platypush.message.event.camera.CameraVideoRenderedEvent`
            when a sequence of captured is successfully rendered into a video
        * :class:`platypush.message.event.camera.CameraPictureTakenEvent`
            when a snapshot is captured and stored to an image file

    """

    _camera_class = Camera
    _camera_info_class = CameraInfo
    _video_writer_class = FFmpegFileWriter

    def __init__(self, device: Optional[Union[int, str]] = None, resolution: Tuple[int, int] = (640, 480),
                 frames_dir: Optional[str] = None, warmup_frames: int = 5, warmup_seconds: Optional[float] = 0.,
                 capture_timeout: Optional[float] = 20.0, scale_x: Optional[float] = None,
                 scale_y: Optional[float] = None, rotate: Optional[float] = None, grayscale: Optional[bool] = None,
                 color_transform: Optional[Union[int, str]] = None, fps: float = 16, horizontal_flip: bool = False,
                 vertical_flip: bool = False, input_format: Optional[str] = None, output_format: Optional[str] = None,
                 stream_format: str = 'mjpeg', listen_port: Optional[int] = 5000, bind_address: str = '0.0.0.0',
                 ffmpeg_bin: str = 'ffmpeg', input_codec: Optional[str] = None, output_codec: Optional[str] = None,
                 **kwargs):
        """
        :param device: Identifier of the default capturing device.
        :param resolution: Default resolution, as a tuple of two integers.
        :param frames_dir: Directory where the camera frames will be stored (default:
            ``~/.local/share/platypush/<plugin.name>/frames``)
        :param warmup_frames: Cameras usually take a while to adapt their
            luminosity and focus to the environment when taking a picture.
            This parameter allows you to specify the number of "warmup" frames
            to capture upon picture command before actually capturing a frame
            (default: 5 but you may want to calibrate this parameter for your
            camera)
        :param warmup_seconds: Number of seconds to wait before a picture is taken or the first frame of a
            video/sequence is captured (default: 0).
        :param capture_timeout: Maximum number of seconds to wait between the programmed termination of a capture
            session and the moment the device is released.
        :param scale_x: If set, the images will be scaled along the x axis by the specified factor
        :param scale_y: If set, the images will be scaled along the y axis by the specified factor
        :param color_transform: Color transformation to apply to the images.
        :param grayscale: Whether the output should be converted to grayscale.
        :param rotate: If set, the images will be rotated by the specified number of degrees
        :param fps: Frames per second (default: 25).
        :param horizontal_flip: If set, the images will be flipped on the horizontal axis.
        :param vertical_flip: If set, the images will be flipped on the vertical axis.
        :param listen_port: Default port to be used for streaming over TCP (default: 5000).
        :param bind_address: Default bind address for TCP streaming (default: 0.0.0.0, accept any connections).
        :param input_codec: Specify the ffmpeg video codec (``-vcodec``) used for the input.
        :param output_codec: Specify the ffmpeg video codec (``-vcodec``) to be used for encoding the output. For some
            ffmpeg output formats (e.g. ``h264`` and ``rtp``) this may default to ``libxvid``.
        :param input_format: Plugin-specific format/type for the input stream.
        :param output_format: Plugin-specific format/type for the output videos.
        :param ffmpeg_bin: Path to the ffmpeg binary (default: ``ffmpeg``).
        :param stream_format: Default format for the output when streamed to a network device. Available:

            - ``MJPEG`` (default)
            - ``H264`` (over ``ffmpeg``)
            - ``H265`` (over ``ffmpeg``)
            - ``MKV`` (over ``ffmpeg``)
            - ``MP4`` (over ``ffmpeg``)

        """
        super().__init__(**kwargs)

        self.workdir = os.path.join(Config.get('workdir'), get_plugin_name_by_class(self))
        pathlib.Path(self.workdir).mkdir(mode=0o755, exist_ok=True, parents=True)

        # noinspection PyArgumentList
        self.camera_info = self._camera_info_class(device, color_transform=color_transform, warmup_frames=warmup_frames,
                                                   warmup_seconds=warmup_seconds, rotate=rotate, scale_x=scale_x,
                                                   scale_y=scale_y, capture_timeout=capture_timeout, fps=fps,
                                                   input_format=input_format, output_format=output_format,
                                                   stream_format=stream_format, resolution=resolution,
                                                   grayscale=grayscale, listen_port=listen_port,
                                                   horizontal_flip=horizontal_flip, vertical_flip=vertical_flip,
                                                   ffmpeg_bin=ffmpeg_bin, input_codec=input_codec,
                                                   output_codec=output_codec, bind_address=bind_address,
                                                   frames_dir=os.path.abspath(
                                                       os.path.expanduser(frames_dir or
                                                                          os.path.join(self.workdir, 'frames'))))

        self._devices: Dict[Union[int, str], Camera] = {}
        self._streams: Dict[Union[int, str], Camera] = {}

    def _merge_info(self, **info) -> CameraInfo:
        merged_info = self.camera_info.clone()
        merged_info.set(**info)
        return merged_info

    def open_device(self, device: Optional[Union[int, str]] = None, stream: bool = False, **params) -> Camera:
        """
        Initialize and open a device.

        :return: The initialized camera device.
        :raises: :class:`platypush.plugins.camera.CaptureSessionAlreadyRunningException`
        """
        info = self._merge_info(**params)
        if device is None:
            device = info.device
        elif device not in self._devices:
            info.device = device
        else:
            info = self._devices[device].info.clone()

        assert device is not None, 'No device specified/configured'
        if device in self._devices:
            camera = self._devices[device]
            if camera.capture_thread and camera.capture_thread.is_alive() and camera.start_event.is_set():
                raise CaptureAlreadyRunningException(device)

            camera.start_event.clear()
            camera.capture_thread = None
        else:
            # noinspection PyArgumentList
            camera = self._camera_class(info=info)

        camera.info.set(**params)
        camera.object = self.prepare_device(camera)

        if stream:
            writer_class = StreamWriter.get_class_by_name(camera.info.stream_format)
            camera.stream = writer_class(camera=camera, plugin=self)

        if camera.info.frames_dir:
            pathlib.Path(os.path.abspath(os.path.expanduser(camera.info.frames_dir))).mkdir(
                mode=0o755, exist_ok=True, parents=True)

        self._devices[device] = camera
        return camera

    def close_device(self, camera: Camera, wait_capture: bool = True) -> None:
        """
        Close and release a device.
        """
        name = camera.info.device
        self.stop_preview(camera)
        self.release_device(camera)

        camera.start_event.clear()
        if wait_capture:
            self.wait_capture(camera)

        if name in self._devices:
            del self._devices[name]

    def wait_capture(self, camera: Camera) -> None:
        """
        Wait until a capture session terminates.

        :param camera: Camera object. ``camera.info.capture_timeout`` is used as a capture thread termination timeout
            if set.
        """
        if camera.capture_thread and camera.capture_thread.is_alive() and \
                threading.get_ident() != camera.capture_thread.ident:
            try:
                camera.capture_thread.join(timeout=camera.info.capture_timeout)
            except Exception as e:
                self.logger.warning('Error on FFmpeg capture wait: {}'.format(str(e)))

    @contextmanager
    def open(self, device: Optional[Union[int, str]] = None, stream: bool = None, **info) -> Camera:
        """
        Initialize and open a device using a context manager pattern.

        :param device: Capture device by name, path or ID.
        :param stream: If set, the frames will be streamed to ``camera.stream``.
        :param info: Camera parameters override - see constructors parameters.
        :return: The initialized :class:`platypush.plugins.camera.Camera` object.
        """
        camera = None
        try:
            camera = self.open_device(device, stream=stream, **info)
            yield camera
        finally:
            self.close_device(camera)

    @abstractmethod
    def prepare_device(self, device: Camera):
        """
        Prepare a device using the plugin-specific logic - to be implemented by the derived classes.

        :param device: An initialized :class:`platypush.plugins.camera.Camera` object.
        """
        raise NotImplementedError()

    @abstractmethod
    def release_device(self, device: Camera):
        """
        Release a device using the plugin-specific logic - to be implemented by the derived classes.

        :param device: An initialized :class:`platypush.plugins.camera.Camera` object.
        """
        raise NotImplementedError()

    @abstractmethod
    def capture_frame(self, device: Camera, *args, **kwargs):
        """
        Capture a frame from a device using the plugin-specific logic - to be implemented by the derived classes.

        :param device: An initialized :class:`platypush.plugins.camera.Camera` object.
        """
        raise NotImplementedError()

    # noinspection PyShadowingBuiltins
    @staticmethod
    def store_frame(frame, filepath: str, format: Optional[str] = None):
        """
        Capture a frame to the filesystem using the ``PIL`` library - it can be overridden by derived classes.

        :param frame: Frame object (default: a byte-encoded object or a ``PIL.Image`` object).
        :param filepath: Destination file.
        :param format: Output format.
        """
        from PIL import Image
        if isinstance(frame, bytes):
            frame = list(frame)
        elif not isinstance(frame, Image.Image):
            frame = Image.fromarray(frame)

        save_args = {}
        if format:
            save_args['format'] = format

        frame.save(filepath, **save_args)

    def _store_frame(self, frame, frames_dir: Optional[str] = None, image_file: Optional[str] = None,
                     *args, **kwargs) -> str:
        """
        :meth:`.store_frame` wrapper.
        """
        if image_file:
            filepath = os.path.abspath(os.path.expanduser(image_file))
        else:
            filepath = os.path.abspath(os.path.expanduser(
                os.path.join(frames_dir or '', datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f.jpg'))))

        pathlib.Path(filepath).parent.mkdir(mode=0o755, exist_ok=True, parents=True)
        self.store_frame(frame, filepath, *args, **kwargs)
        return filepath

    def start_preview(self, camera: Camera):
        if camera.preview and not camera.preview.closed:
            self.logger.info('A preview window is already active on device {}'.format(camera.info.device))
            return

        camera.preview = PreviewWriterFactory.get(camera, self)
        if isinstance(camera.preview, Process):
            camera.preview.start()

    def stop_preview(self, camera: Camera):
        if camera.preview and not camera.preview.closed:
            camera.preview.close()

        if isinstance(camera.preview, Process) and camera.preview.is_alive():
            camera.preview.terminate()
            camera.preview.join(timeout=5.0)

        if isinstance(camera.preview, Process) and camera.preview.is_alive():
            camera.preview.kill()

        camera.preview = None

    def frame_processor(self, frame_queue: Queue, camera: Camera, image_file: Optional[str] = None):
        while True:
            frame = frame_queue.get()
            if frame is None:
                break

            frame = self.transform_frame(frame, camera.info.color_transform)
            if camera.info.grayscale:
                frame = self.to_grayscale(frame)

            frame = self.rotate_frame(frame, camera.info.rotate)
            frame = self.flip_frame(frame, camera.info.horizontal_flip, camera.info.vertical_flip)
            frame = self.scale_frame(frame, camera.info.scale_x, camera.info.scale_y)

            for output in camera.get_outputs():
                output.write(frame)

            if camera.info.frames_dir or image_file:
                self._store_frame(frame=frame, frames_dir=camera.info.frames_dir, image_file=image_file)

    def capturing_thread(self, camera: Camera, duration: Optional[float] = None, video_file: Optional[str] = None,
                         image_file: Optional[str] = None, n_frames: Optional[int] = None, preview: bool = False,
                         **kwargs):
        """
        Camera capturing thread.

        :param camera: An initialized :class:`platypush.plugins.camera.Camera` object.
        :param duration: Capturing session duration in seconds (default: until :meth:`.stop_capture` is called).
        :param video_file: If set, the session will be recorded to this output video file (video capture mode).
        :param image_file: If set, the output of the session will be a single image file (photo mode).
        :param n_frames: Number of frames to be captured (default: until :meth:`.stop_capture` is called).
        :param preview: Start a preview window.
        :param kwargs: Extra arguments to be passed to :meth:`.capture_frame`.
        """
        camera.start_event.wait()
        recording_started_time = time.time()
        captured_frames = 0

        evt_args = {
            'device': camera.info.device,
        }

        if video_file or image_file:
            evt_args['filename'] = video_file or image_file
        if camera.info.frames_dir:
            evt_args['frames_dir'] = camera.info.frames_dir
        if preview:
            self.start_preview(camera)
        if duration and camera.info.warmup_seconds:
            duration = duration + camera.info.warmup_seconds
        if video_file:
            camera.file_writer = self._video_writer_class(camera=camera, plugin=self, output_file=video_file)

        frame_queue = Queue()
        frame_processor = threading.Thread(target=self.frame_processor,
                                           kwargs=dict(frame_queue=frame_queue, camera=camera, image_file=image_file))
        frame_processor.start()
        self.fire_event(CameraRecordingStartedEvent(**evt_args))

        try:
            while camera.start_event.is_set():
                if (duration and time.time() - recording_started_time >= duration) \
                        or (n_frames and captured_frames >= n_frames):
                    break

                frame_capture_start = time.time()
                try:
                    frame = self.capture_frame(camera, **kwargs)
                    if not frame:
                        self.logger.warning('Invalid frame received, terminating the capture session')
                        break

                    frame_queue.put(frame)
                except AssertionError as e:
                    self.logger.warning(str(e))
                    continue

                if not n_frames or not camera.info.warmup_seconds or \
                        (time.time() - recording_started_time >= camera.info.warmup_seconds):
                    captured_frames += 1

                if camera.info.fps:
                    wait_time = (1. / camera.info.fps) - (time.time() - frame_capture_start)
                    if wait_time > 0:
                        time.sleep(wait_time)
        finally:
            frame_queue.put(None)
            self.stop_preview(camera)
            for output in camera.get_outputs():
                # noinspection PyBroadException
                try:
                    output.close()
                except:
                    pass

            self.close_device(camera, wait_capture=False)
            frame_processor.join(timeout=5.0)
            self.fire_event(CameraRecordingStoppedEvent(**evt_args))

        if image_file:
            self.fire_event(CameraPictureTakenEvent(filename=image_file))

        if video_file:
            self.fire_event(CameraVideoRenderedEvent(filename=video_file))

    def start_camera(self, camera: Camera, preview: bool = False, *args, **kwargs):
        """
        Start a camera capture session.

        :param camera: An initialized :class:`platypush.plugins.camera.Camera` object.
        :param preview: Show a preview of the camera frames.
        """
        assert not (camera.capture_thread and camera.capture_thread.is_alive()), \
            'A capture session is already in progress'

        camera.capture_thread = threading.Thread(target=self.capturing_thread, args=(camera, *args),
                                                 kwargs={'preview': preview, **kwargs})
        camera.capture_thread.start()
        camera.start_event.set()

    @action
    def capture_video(self, duration: Optional[float] = None, video_file: Optional[str] = None, preview: bool = False,
                      **camera) -> Union[str, dict]:
        """
        Capture a video.

        :param duration: Record duration in seconds (default: None, record until ``stop_capture``).
        :param video_file: If set, the stream will be recorded to the specified video file (default: None).
        :param camera: Camera parameters override - see constructors parameters.
        :param preview: Show a preview of the camera frames.
        :return: If duration is specified, the method will wait until the recording is done and return the local path
            to the recorded resource. Otherwise, it will return the status of the camera device after starting it.
        """
        camera = self.open_device(**camera)
        self.start_camera(camera, duration=duration, video_file=video_file, frames_dir=None, image_file=None,
                          preview=preview)

        if duration:
            self.wait_capture(camera)
            return video_file

        return self.status(camera.info.device)

    @action
    def stop_capture(self, device: Optional[Union[int, str]] = None):
        """
        Stop any capturing session on the specified device.

        :param device: Name/path/ID of the device to stop (default: all the active devices).
        """
        devices = self._devices.copy()
        stop_devices = list(devices.values())[:]
        if device:
            stop_devices = [self._devices[device]] if device in self._devices else []

        for device in stop_devices:
            self.close_device(device)

    @action
    def capture_image(self, image_file: str, preview: bool = False, **camera) -> str:
        """
        Capture an image.

        :param image_file: Path where the output image will be stored.
        :param camera: Camera parameters override - see constructors parameters.
        :param preview: Show a preview of the camera frames.
        :return: The local path to the saved image.
        """

        with self.open(**camera) as camera:
            warmup_frames = camera.info.warmup_frames if camera.info.warmup_frames else 1
            self.start_camera(camera, image_file=image_file, n_frames=warmup_frames, preview=preview)
            self.wait_capture(camera)

        return image_file

    @action
    def take_picture(self, image_file: str, preview: bool = False, **camera) -> str:
        """
        Alias for :meth:`.capture_image`.

        :param image_file: Path where the output image will be stored.
        :param camera: Camera parameters override - see constructors parameters.
        :param preview: Show a preview of the camera frames.
        :return: The local path to the saved image.
        """
        return self.capture_image(image_file, **camera)

    @action
    def capture_sequence(self, duration: Optional[float] = None, n_frames: Optional[int] = None, preview: bool = False,
                         **camera) -> str:
        """
        Capture a sequence of frames from a camera and store them to a directory.

        :param duration: Duration of the sequence in seconds (default: until :meth:`.stop_capture` is called).
        :param n_frames: Number of images to be captured (default: until :meth:`.stop_capture` is called).
        :param camera: Camera parameters override - see constructors parameters. ``frames_dir`` and ``fps`` in
            particular can be specifically tuned for ``capture_sequence``.
        :param preview: Show a preview of the camera frames.
        :return: The directory where the image files have been stored.
        """
        with self.open(**camera) as camera:
            self.start_camera(camera, duration=duration, n_frames=n_frames, preview=preview)
            self.wait_capture(camera)
            return camera.info.frames_dir

    @action
    def capture_preview(self, duration: Optional[float] = None, n_frames: Optional[int] = None, **camera) -> dict:
        """
        Start a camera preview session.

        :param duration: Preview duration (default: until :meth:`.stop_capture` is called).
        :param n_frames: Number of frames to display before closing (default: until :meth:`.stop_capture` is called).
        :param camera: Camera object properties.
        :return: The status of the device.
        """
        camera = self.open_device(frames_dir=None, **camera)
        self.start_camera(camera, duration=duration, n_frames=n_frames, preview=True)
        return self.status(camera.info.device)

    @staticmethod
    def _prepare_server_socket(camera: Camera) -> socket.socket:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((camera.info.bind_address or '0.0.0.0', camera.info.listen_port))
        server_socket.listen(1)
        server_socket.settimeout(1)
        return server_socket

    def _accept_client(self, server_socket: socket.socket) -> Optional[IO]:
        try:
            sock = server_socket.accept()[0]
            self.logger.info('Accepted client connection from {}'.format(sock.getpeername()))
            return sock.makefile('wb')
        except socket.timeout:
            return

    def streaming_thread(self, camera: Camera, stream_format: str, duration: Optional[float] = None):
        streaming_started_time = time.time()
        server_socket = self._prepare_server_socket(camera)
        sock = None
        self.logger.info('Starting streaming on port {}'.format(camera.info.listen_port))

        try:
            while camera.stream_event.is_set():
                if duration and time.time() - streaming_started_time >= duration:
                    break

                sock = self._accept_client(server_socket)
                if not sock:
                    continue

                if camera.info.device not in self._devices:
                    info = camera.info.to_dict()
                    info['stream_format'] = stream_format
                    camera = self.open_device(stream=True, **info)

                camera.stream.sock = sock
                self.start_camera(camera, duration=duration, frames_dir=None, image_file=None)
        finally:
            self._cleanup_stream(camera, server_socket, sock)
            self.logger.info('Stopped camera stream')

    def _cleanup_stream(self, camera: Camera, server_socket: socket.socket, client: IO):
        if client:
            try:
                client.close()
            except Exception as e:
                self.logger.warning('Error on client socket close: {}'.format(str(e)))

        try:
            server_socket.close()
        except Exception as e:
            self.logger.warning('Error on server socket close: {}'.format(str(e)))

        if camera.stream:
            try:
                camera.stream.close()
            except Exception as e:
                self.logger.warning('Error while closing the encoding stream: {}'.format(str(e)))

    @action
    def start_streaming(self, duration: Optional[float] = None, stream_format: str = 'mkv', **camera) -> dict:
        """
        Expose the video stream of a camera over a TCP connection.

        :param duration: Streaming thread duration (default: until :meth:`.stop_streaming` is called).
        :param stream_format: Format of the output stream - e.g. ``h264``, ``mjpeg``, ``mkv`` etc. (default: ``mkv``).
        :param camera: Camera object properties - see constructor parameters.
        :return: The status of the device.
        """
        camera = self.open_device(stream=True, stream_format=stream_format, **camera)
        return self._start_streaming(camera, duration, stream_format)

    def _start_streaming(self, camera: Camera, duration: Optional[float], stream_format: str):
        assert camera.info.listen_port, 'No listen_port specified/configured'
        assert not camera.stream_event.is_set() and camera.info.device not in self._streams, \
            'A streaming session is already running for device {}'.format(camera.info.device)

        self._streams[camera.info.device] = camera
        camera.stream_event.set()

        camera.stream_thread = threading.Thread(target=self.streaming_thread, kwargs=dict(
            camera=camera, duration=duration, stream_format=stream_format))
        camera.stream_thread.start()
        return self.status(camera.info.device)

    @action
    def stop_streaming(self, device: Optional[Union[int, str]] = None):
        """
        Stop a camera over TCP session.

        :param device: Name/path/ID of the device to stop (default: all the active devices).
        """
        streams = self._streams.copy()
        stop_devices = list(streams.values())[:]
        if device:
            stop_devices = [self._streams[device]] if device in self._streams else []

        for device in stop_devices:
            self._stop_streaming(device)

    def _stop_streaming(self, camera: Camera):
        camera.stream_event.clear()
        if camera.stream_thread and camera.stream_thread.is_alive():
            camera.stream_thread.join(timeout=5.0)

        if camera.info.device in self._streams:
            del self._streams[camera.info.device]

    def _status(self, device: Union[int, str]) -> dict:
        camera = self._devices.get(device, self._streams.get(device))
        if not camera:
            return {}

        return {
            **camera.info.to_dict(),
            'active': True if camera.capture_thread and camera.capture_thread.is_alive() else False,
            'capturing': True if camera.capture_thread and camera.capture_thread.is_alive() and camera.start_event.is_set() else False,
            'streaming': camera.stream_thread and camera.stream_thread.is_alive() and camera.stream_event.is_set(),
        }

    @action
    def status(self, device: Optional[Union[int, str]] = None):
        """
        Returns the status of the specified camera or all the active cameras if ``device`` is ``None``.
        """

        if device:
            return self._status(device)

        return {
            id: self._status(device)
            for id, camera in self._devices.items()
        }

    @staticmethod
    def transform_frame(frame, color_transform):
        """
        Frame color space (e.g. ``RGB24``, ``YUV`` etc.) transform logic. Does nothing unless implemented by a
        derived plugin.
        """
        return frame.convert(color_transform)

    def to_grayscale(self, frame):
        """
        Convert a frame to grayscale. The default implementation assumes that frame is a ``PIL.Image`` object.

        :param frame: Image frame (default: a ``PIL.Image`` object).
        """
        from PIL import ImageOps
        return ImageOps.grayscale(frame)

    @staticmethod
    def rotate_frame(frame, rotation: Optional[Union[float, int]] = None):
        """
        Frame rotation logic. The default implementation assumes that frame is a ``PIL.Image`` object.

        :param frame: Image frame (default: a ``PIL.Image`` object).
        :param rotation: Rotation angle in degrees.
        """
        if not rotation:
            return frame

        return frame.rotate(rotation, expand=True)

    @staticmethod
    def flip_frame(frame, horizontal_flip: bool = False, vertical_flip: bool = False):
        """
        Frame flip logic. Does nothing unless implemented by a derived plugin.

        :param frame: Image frame (default: a ``PIL.Image`` object).
        :param horizontal_flip: Flip along the horizontal axis.
        :param vertical_flip: Flip along the vertical axis.
        """
        from PIL import Image

        if horizontal_flip:
            frame = frame.transpose(Image.FLIP_TOP_BOTTOM)
        if vertical_flip:
            frame = frame.transpose(Image.FLIP_LEFT_RIGHT)

        return frame

    @staticmethod
    def scale_frame(frame, scale_x: Optional[float] = None, scale_y: Optional[float] = None):
        """
        Frame scaling logic. The default implementation assumes that frame is a ``PIL.Image`` object.

        :param frame: Image frame (default: a ``PIL.Image`` object).
        :param scale_x: X-scale factor.
        :param scale_y: Y-scale factor.
        """
        from PIL import Image
        if not (scale_x and scale_y) or (scale_x == 1 and scale_y == 1):
            return frame

        size = (int(frame.size[0] * scale_x), int(frame.size[1] * scale_y))
        return frame.resize(size, Image.ANTIALIAS)

    @staticmethod
    def encode_frame(frame, encoding: str = 'jpeg') -> bytes:
        """
        Encode a frame to a target type. The default implementation assumes that frame is a ``PIL.Image`` object.

        :param frame: Image frame (default: a ``PIL.Image`` object).
        :param encoding: Image encoding (e.g. ``jpeg``).
        """
        if not encoding:
            return frame

        with io.BytesIO() as buf:
            frame.save(buf, format=encoding)
            return buf.getvalue()

    @staticmethod
    def _get_warmup_seconds(camera: Camera) -> float:
        if camera.info.warmup_seconds:
            return camera.info.warmup_seconds
        if camera.info.warmup_frames and camera.info.fps:
            return camera.info.warmup_frames / camera.info.fps
        return 0


# vim:sw=4:ts=4:et:
