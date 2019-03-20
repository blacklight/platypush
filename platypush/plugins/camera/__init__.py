import os
import re
import shutil
import threading
import time

import cv2

from datetime import datetime

from platypush.config import Config
from platypush.message.response import Response
from platypush.message.event.camera import CameraRecordingStartedEvent, \
    CameraRecordingStoppedEvent, CameraVideoRenderedEvent, \
    CameraPictureTakenEvent, CameraFrameCapturedEvent, CameraEvent

from platypush.plugins import Plugin, action


class CameraPlugin(Plugin):
    """
    Plugin to control generic cameras over OpenCV.

    Triggers:

        * :class:`platypush.message.event.camera.CameraRecordingStartedEvent`
            when a new video recording/photo burst starts
        * :class:`platypush.message.event.camera.CameraRecordingStoppedEvent`
            when a video recording/photo burst ends
        * :class:`platypush.message.event.camera.CameraVideoRenderedEvent`
            when a sequence of captured is successfully rendered into a video
        * :class:`platypush.message.event.camera.CameraPictureTakenEvent`
            when a snapshot is captured and stored to an image file

    Requires:

        * **opencv** (``pip install opencv-python``)
    """

    _default_frames_dir = os.path.join(Config.get('workdir'), 'camera',
                                       'frames')

    _default_warmup_frames = 5
    _default_sleep_between_frames = 0
    _default_color_transform = 'COLOR_BGR2BGRA'

    _max_stored_frames = 100
    _frame_filename_regex = re.compile('(\d+)-(\d+)-(\d+)_(\d+)-(\d+)-(\d+)-(\d+).jpe?g$')

    def __init__(self, device_id=0, frames_dir=_default_frames_dir,
                 warmup_frames=_default_warmup_frames, video_type=0,
                 sleep_between_frames=_default_sleep_between_frames,
                 max_stored_frames=_max_stored_frames,
                 color_transform=_default_color_transform,
                 scale_x=None, scale_y=None, rotate=None, flip=None,
                 *args, **kwargs):
        """
        :param device_id: Index of the default video device to be used for
            capturing (default: 0)
        :type device_id: int

        :param frames_dir: Directory where the camera frames will be stored
            (default: ``~/.local/share/platypush/camera/frames``)
        :type frames_dir: str

        :param warmup_frames: Cameras usually take a while to adapt their
            luminosity and focus to the environment when taking a picture.
            This parameter allows you to specify the number of "warmup" frames
            to capture upon picture command before actually capturing a frame
            (default: 5 but you may want to calibrate this parameter for your
            camera)
        :type warmup_frames: int

        :param video_type: Default video type to use when exporting captured
            frames to camera (default: 0, infers the type from the video file
            extension). See https://docs.opencv.org/4.0.1/dd/d9e/classcv_1_1VideoWriter.html#afec93f94dc6c0b3e28f4dd153bc5a7f0
            for a reference on the supported types (e.g. 'MJPEG', 'XVID', 'H264' etc')
        :type video_type: str or int

        :param sleep_between_frames: If set, the process will sleep for the
            specified amount of seconds between two frames when recording
            (default: 0)
        :type sleep_between_frames: float

        :param max_stored_frames: Maximum number of frames to store in
            ``frames_dir`` when recording with no persistence (e.g. streaming
            over HTTP) (default: 100)
        :type max_stored_frames: int

        :param color_transform: Color transformation to apply to the captured
            frames. See https://docs.opencv.org/3.2.0/d7/d1b/group__imgproc__misc.html
            for a full list of supported color transformations.
            (default: "``COLOR_BGR2BGRA``")
        :type color_transform: str

        :param scale_x: If set, the images will be scaled along the x axis by the
            specified factor
        :type scale_x: float

        :param scale_y: If set, the images will be scaled along the y axis by the
            specified factor
        :type scale_y: float

        :param rotate: If set, the images will be rotated by the specified
            number of degrees
        :type rotate: float

        :param flip: If set, the images will be flipped around the specified
            axis. Possible values::

                - ``0`` - flip along the x axis
                - ``1`` - flip along the y axis
                - ``-1`` - flip along both the axis

        :type flip: int
        """

        super().__init__(*args, **kwargs)

        self.default_device_id = device_id
        self.frames_dir = os.path.abspath(os.path.expanduser(frames_dir))
        self.warmup_frames = warmup_frames
        self.video_type = cv2.VideoWriter_fourcc(*video_type) \
            if isinstance(video_type, str) else video_type

        self.sleep_between_frames = sleep_between_frames
        self.max_stored_frames = max_stored_frames
        self.color_transform = color_transform
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.rotate = rotate
        self.flip = flip

        self._is_recording = {}   # device_id => Event map
        self._devices = {}   # device_id => VideoCapture map
        self._recording_threads = {}    # device_id => Thread map
        self._recording_info = {}   # device_id => recording info map

    def _init_device(self, device_id, frames_dir=None, **info):
        self._release_device(device_id)

        if device_id not in self._devices:
            self._devices[device_id] = cv2.VideoCapture(device_id)

        if device_id not in self._is_recording:
            self._is_recording[device_id] = threading.Event()

        self._recording_info[device_id] = info

        if frames_dir:
            os.makedirs(frames_dir, exist_ok=True)
            self._recording_info[device_id]['frames_dir'] = frames_dir

        return self._devices[device_id]


    def _release_device(self, device_id, wait_thread_termination=True):
        if device_id in self._is_recording:
            self._is_recording[device_id].clear()

        if device_id in self._recording_threads:
            if wait_thread_termination:
                self.logger.info('A recording thread is running, waiting for termination')
                if self._recording_threads[device_id].is_alive():
                    self._recording_threads[device_id].join()
                del self._recording_threads[device_id]

        if device_id in self._devices:
            self._devices[device_id].release()
            del self._devices[device_id]
            self.fire_event(CameraRecordingStoppedEvent(device_id=device_id))
            self.logger.info("Device {} released".format(device_id))

        if device_id in self._recording_info:
            del self._recording_info[device_id]


    def _store_frame_to_file(self, frame, frames_dir, image_file):
        if image_file:
            filepath = image_file
        else:
            filepath = os.path.join(
                frames_dir, datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f.jpg'))

        cv2.imwrite(filepath, frame)
        return filepath


    def _get_stored_frames_files(self, frames_dir):
        ret = sorted([
            os.path.join(frames_dir, f) for f in os.listdir(frames_dir)
            if os.path.isfile(os.path.join(frames_dir, f)) and
            re.search(self._frame_filename_regex, f)
        ])
        return ret


    def _get_avg_fps(self, frames_dir):
        files = self._get_stored_frames_files(frames_dir)
        frame_time_diff = 0.0
        n_frames = 0

        for i in range(1, len(files)):
            m1 = re.search(self._frame_filename_regex, files[i-1])
            m2 = re.search(self._frame_filename_regex, files[i])

            if not m1 or not m2:
                continue

            t1 = datetime.timestamp(datetime(*map(int, m1.groups())))
            t2 = datetime.timestamp(datetime(*map(int, m2.groups())))
            frame_time_diff += (t2-t1)
            n_frames += 1

        return n_frames/frame_time_diff if n_frames and frame_time_diff else 0


    def _remove_expired_frames(self, frames_dir, max_stored_frames):
        files = self._get_stored_frames_files(frames_dir)
        for f in files[:len(files)-max_stored_frames]:
            os.unlink(f)


    def _make_video_file(self, frames_dir, video_file, video_type):
        files = self._get_stored_frames_files(frames_dir)
        if not files:
            self.logger.warning('No frames found in {}'.format(frames_dir))
            return

        frame = cv2.imread(files[0])
        height, width, layers = frame.shape
        fps = self._get_avg_fps(frames_dir)
        video = cv2.VideoWriter(video_file, video_type, fps, (width, height))

        for f in files:
            video.write(cv2.imread(f))
        video.release()

        self.fire_event(CameraVideoRenderedEvent(filename=video_file))
        shutil.rmtree(frames_dir, ignore_errors=True)


    def _recording_thread(self):
        def thread(duration, video_file, image_file, device_id,
                   frames_dir, n_frames, sleep_between_frames,
                   max_stored_frames, color_transform, video_type,
                   scale_x, scale_y, rotate, flip):

            device = self._devices[device_id]
            color_transform = getattr(cv2, self.color_transform)
            rotation_matrix = None
            self._is_recording[device_id].wait()
            self.logger.info('Starting recording from video device {}'.
                             format(device_id))
            recording_started_time = time.time()
            captured_frames = 0

            evt_args = {
                'device_id': device_id,
            }

            if video_file or image_file:
                evt_args['filename'] = video_file or image_file
            if frames_dir:
                evt_args['frames_dir'] = frames_dir

            self.fire_event(CameraRecordingStartedEvent(**evt_args))

            while device_id in self._is_recording and self._is_recording[device_id].is_set():
                if duration and time.time() - recording_started_time >= duration \
                        or n_frames and captured_frames >= n_frames:
                    break

                ret, frame = device.read()
                if not ret:
                    self.logger.warning('Error while retrieving video frame')
                    continue

                frame = cv2.cvtColor(frame, color_transform)

                if rotate:
                    rows, cols = frame.shape
                    if not rotation_matrix:
                        rotation_matrix = cv2.getRotationMatrix2D(
                            (cols/2, rows/2), rotate, 1)

                    frame = cv2.warpAffine(frame, rotation_matrix, (cols, rows))

                if flip is not None:
                    frame = cv2.flip(frame, flip)

                if scale_x or scale_y:
                    scale_x = scale_x or 1
                    scale_y = scale_y or 1
                    frame = cv2.resize(frame, None, fx=scale_x, fy=scale_y,
                                       interpolation = cv2.INTER_CUBIC)

                self._store_frame_to_file(frame=frame, frames_dir=frames_dir,
                                          image_file=image_file)
                captured_frames += 1
                self.fire_event(CameraFrameCapturedEvent(filename=image_file))

                if max_stored_frames and not video_file:
                    self._remove_expired_frames(
                        frames_dir=frames_dir,
                        max_stored_frames=max_stored_frames)

                if sleep_between_frames:
                    time.sleep(sleep_between_frames)

            self._release_device(device_id, wait_thread_termination=False)

            if image_file:
                self.fire_event(CameraPictureTakenEvent(filename=image_file))

            self.logger.info('Recording terminated')

            if video_file:
                self.logger.info('Writing frames to video file {}'.
                                 format(video_file))
                self._make_video_file(frames_dir=frames_dir,
                                      video_file=video_file,
                                      video_type=video_type)
                self.logger.info('Video file {}: rendering completed'.
                                 format(video_file))

        return thread


    @action
    def start_recording(self, duration=None, video_file=None, video_type=None,
                        device_id=None, frames_dir=None,
                        sleep_between_frames=None, max_stored_frames=None,
                        color_transform=None, scale_x=None, scale_y=None,
                        rotate=None, flip=None):
        """
        Start recording

        :param duration: Record duration in seconds (default: None, record until
            ``stop_recording``)
        :type duration: float

        :param video_file: If set, the stream will be recorded to the specified
            video file (default: None)
        :type video_file: str

        :param video_type: Overrides the default configured ``video_type``
        :type video_file: str

        :param device_id, frames_dir, sleep_between_frames, max_stored_frames,
            color_transform, scale_x, scale_y, rotate, flip: Set
            these parameters if you want to override the default configured ones.
        """

        device_id = device_id if device_id is not None else self.default_device_id
        if device_id in self._is_recording and \
                self._is_recording[device_id].is_set():
            self.logger.info('A recording on device {} is already in progress'.
                             format(device_id))
            return self.status(device_id=device_id)

        recording_started = threading.Event()
        def on_recording_started(event):
            recording_started.set()

        frames_dir = os.path.abspath(os.path.expanduser(frames_dir)) \
            if frames_dir is not None else self.frames_dir
        sleep_between_frames = sleep_between_frames if sleep_between_frames \
            is not None else self.sleep_between_frames
        max_stored_frames = max_stored_frames if max_stored_frames \
            is not None else self.max_stored_frames
        color_transform = color_transform if color_transform \
            is not None else self.color_transform
        scale_x = scale_x if scale_x is not None else self.scale_x
        scale_y = scale_y if scale_y is not None else self.scale_y
        rotate = rotate if rotate is not None else self.rotate
        flip = flip if flip is not None else self.flip

        if video_type is not None:
            video_type = cv2.VideoWriter_fourcc(*video_type.upper()) \
                if isinstance(video_type, str) else video_type
        else:
            video_type = self.video_type

        frames_dir = os.path.join(frames_dir, str(device_id))
        if video_file:
            video_file = os.path.abspath(os.path.expanduser(video_file))
            frames_dir = os.path.join(frames_dir, 'recording_{}'.format(
                datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')))

        self._init_device(device_id, video_file=video_file,
                          video_type=video_type,
                          frames_dir=frames_dir,
                          sleep_between_frames=sleep_between_frames,
                          max_stored_frames=max_stored_frames,
                          color_transform=color_transform, scale_x=scale_x,
                          scale_y=scale_y, rotate=rotate, flip=flip)

        self.register_handler(CameraRecordingStartedEvent, on_recording_started)

        self._recording_threads[device_id] = threading.Thread(
            target=self._recording_thread(), kwargs = {
                'duration':duration,
                'video_file':video_file,
                'video_type':video_type,
                'image_file':None, 'device_id':device_id,
                'frames_dir':frames_dir, 'n_frames':None,
                'sleep_between_frames':sleep_between_frames,
                'max_stored_frames':max_stored_frames,
                'color_transform':color_transform,
                'scale_x':scale_x, 'scale_y':scale_y,
                'rotate':rotate, 'flip':flip
            })

        self._recording_threads[device_id].start()
        self._is_recording[device_id].set()

        recording_started.wait()
        self.unregister_handler(CameraRecordingStartedEvent, on_recording_started)
        return self.status(device_id=device_id)

    @action
    def stop_recording(self, device_id=None):
        """
        Stop recording
        """

        device_id = device_id if device_id is not None else self.default_device_id
        frames_dir = self._recording_info.get(device_id, {}).get('frames_dir')
        self._release_device(device_id)
        shutil.rmtree(frames_dir, ignore_errors=True)

    @action
    def take_picture(self, image_file, device_id=None, warmup_frames=None,
                     color_transform=None, scale_x=None, scale_y=None,
                     rotate=None, flip=None):
        """
        Take a picture.

        :param image_file: Path where the output image will be stored.
        :type image_file: str

        :param device_id, warmup_frames, color_transform, scale_x, scale_y,
            rotate, flip: Overrides the configured default parameters
        """

        device_id = device_id if device_id is not None else self.default_device_id
        image_file = os.path.abspath(os.path.expanduser(image_file))
        picture_taken = threading.Event()

        def on_picture_taken(event):
            picture_taken.set()

        if device_id in self._is_recording and \
                self._is_recording[device_id].is_set():
            self.logger.info('A recording on device {} is already in progress'.
                             format(device_id))

            status = self.status(device_id=device_id).output.get(device_id)
            if 'image_file' in status:
                shutil.copyfile(status['image_file'], image_file)
                return { 'path': image_file }

            raise RuntimeError('Recording already in progress and no images ' +
                               'have been captured yet')

        warmup_frames = warmup_frames if warmup_frames is not None else \
            self.warmup_frames
        color_transform = color_transform if color_transform \
            is not None else self.color_transform
        scale_x = scale_x if scale_x is not None else self.scale_x
        scale_y = scale_y if scale_y is not None else self.scale_y
        rotate = rotate if rotate is not None else self.rotate
        flip = flip if flip is not None else self.flip

        self._init_device(device_id, image_file=image_file,
                          warmup_frames=warmup_frames,
                          color_transform=color_transform,
                          scale_x=scale_x, scale_y=scale_y, rotate=rotate,
                          flip=flip)

        self.register_handler(CameraPictureTakenEvent, on_picture_taken)
        self._recording_threads[device_id] = threading.Thread(
            target=self._recording_thread(), kwargs = {
                'duration':None, 'video_file':None,
                'image_file':image_file, 'video_type':None,
                'device_id':device_id, 'frames_dir':None,
                'n_frames':warmup_frames,
                'sleep_between_frames':None,
                'max_stored_frames':None,
                'color_transform':color_transform,
                'scale_x':scale_x, 'scale_y':scale_y,
                'rotate':rotate, 'flip':flip
            })

        self._recording_threads[device_id].start()
        self._is_recording[device_id].set()

        picture_taken.wait()
        self.unregister_handler(CameraPictureTakenEvent, on_picture_taken)
        return { 'path': image_file }

    @action
    def status(self, device_id=None):
        """
        Returns the status of the specified device_id or all the device in a
        ``{ device_id => device_info }`` map format. Device info includes
        ``video_file``, ``image_file``, ``frames_dir`` and additional video info
        """

        resp = Response(output={
            id: {
                'image_file': self._get_stored_frames_files(info['frames_dir'])[-2]
                if 'frames_dir' in info
                and len(self._get_stored_frames_files(info['frames_dir'])) > 1
                and 'image_file' not in info else info.get('image_file'), **info
            }
            for id, info in self._recording_info.items()
            if device_id is None or id == device_id
        }, disable_logging=True)
        return resp


    @action
    def get_default_device_id(self):
        return self.default_device_id


# vim:sw=4:ts=4:et:
