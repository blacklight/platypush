"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
"""

import os
import socket
import threading
import time

from platypush.plugins import action
from platypush.plugins.camera import CameraPlugin


class CameraPiPlugin(CameraPlugin):
    """
    Plugin to control a Pi camera.

    Requires:

        * **picamera** (``pip install picamera``)
    """

    _default_resolution = (800, 600)

    def __init__(self, resolution=(_default_resolution[0], _default_resolution[1]), framerate=24,
                 hflip=False, vflip=False, sharpness=0, contrast=0, brightness=50, video_stabilization=False, iso=0,
                 exposure_compensation=0, exposure_mode='auto', meter_mode='average', awb_mode='auto',
                 image_effect='none', color_effects=None, rotation=0, crop=(0.0, 0.0, 1.0, 1.0), **kwargs):
        """
        See https://www.raspberrypi.org/documentation/usage/camera/python/README.md
        for a detailed reference about the Pi camera options.
        """
        super().__init__(**kwargs)

        self.camera_args = {
            'resolution': tuple(resolution),
            'framerate': framerate,
            'hflip': hflip,
            'vflip': vflip,
            'sharpness': sharpness,
            'contrast': contrast,
            'brightness': brightness,
            'video_stabilization': video_stabilization,
            'ISO': iso,
            'exposure_compensation': exposure_compensation,
            'exposure_mode': exposure_mode,
            'meter_mode': meter_mode,
            'awb_mode': awb_mode,
            'image_effect': image_effect,
            'color_effects': color_effects,
            'rotation': rotation,
            'crop': tuple(crop),
        }

        self._camera = None

        self._time_lapse_thread = None
        self._recording_thread = None
        self._streaming_thread = None
        self._time_lapse_stop_condition = threading.Condition()
        self._recording_stop_condition = threading.Condition()
        self._streaming_stop_condition = threading.Condition()

    # noinspection PyUnresolvedReferences,PyPackageRequirements
    def _get_camera(self, **opts):
        if self._camera:
            return self._camera

        import picamera
        self._camera = picamera.PiCamera()

        for (attr, value) in self.camera_args:
            setattr(self._camera, attr, value)
        for (attr, value) in opts:
            setattr(self._camera, attr, value)

        return self._camera

    @action
    def take_picture(self, image_file, preview=False, warmup_time=2, resize=None, **opts):
        """
        Take a picture.

        :param image_file: Path where the output image will be stored.
        :type image_file: str

        :param preview: Show a preview before taking the picture (default: False)
        :type preview: bool

        :param warmup_time: Time before taking the picture (default: 2 seconds)
        :type warmup_time: float

        :param resize: Set if you want to resize the picture to a new format
        :type resize: list or tuple (with two elements)

        :param opts: Extra options to pass to the camera (see
            https://www.raspberrypi.org/documentation/usage/camera/python/README.md)

        :return: dict::

            {"image_file": path_to_the_image}

        """

        camera = self._get_camera(**opts)
        image_file = os.path.abspath(os.path.expanduser(image_file))

        if preview:
            camera.start_preview()

        if warmup_time:
            time.sleep(warmup_time)

        capture_opts = {}
        if resize:
            capture_opts['resize'] = tuple(resize)

        camera.capture(image_file, **capture_opts)
        return {'image_file': image_file}

    @action
    def capture_sequence(self, n_images, directory, name_format='image_%04d.jpg', preview=False, warmup_time=2,
                         resize=None, **opts):
        """
        Capture a sequence of images

        :param n_images: Number of images to capture
        :type n_images: int

        :param directory: Path where the images will be stored
        :type directory: str

        :param name_format: Format for the name of the stored images. Use %d or any other format string for representing
            the image index (default: image_%04d.jpg)
        :type name_format: str

        :param preview: Show a preview before taking the picture (default: False)
        :type preview: bool

        :param warmup_time: Time before taking the picture (default: 2 seconds)
        :type warmup_time: float

        :param resize: Set if you want to resize the picture to a new format
        :type resize: list or tuple (with two elements)

        :param opts: Extra options to pass to the camera (see
            https://www.raspberrypi.org/documentation/usage/camera/python/README.md)

        :return: dict::

            {"image_files": [list of captured images]}

        """

        camera = self._get_camera(**opts)
        directory = os.path.abspath(os.path.expanduser(directory))

        if preview:
            camera.start_preview()

        if warmup_time:
            time.sleep(warmup_time)
            camera.exposure_mode = 'off'

        camera.shutter_speed = camera.exposure_speed
        g = camera.awb_gains
        camera.awb_mode = 'off'
        camera.awb_gains = g
        capture_opts = {}

        if resize:
            capture_opts['resize'] = tuple(resize)

        images = [os.path.join(directory, name_format % str(i+1)) for i in range(0, n_images)]
        camera.capture_sequence(images, **capture_opts)
        return {'image_files': images}

    @action
    def start_time_lapse(self, directory, n_images=None, interval=0, warmup_time=2,
                         resize=None, **opts):
        """
        Start a time lapse capture

        :param directory: Path where the images will be stored
        :type directory: str

        :param n_images: Number of images to capture (default: None, capture until stop_time_lapse)
        :type n_images: int

        :param interval: Interval in seconds between two pictures (default: 0)
        :type interval: float

        :param warmup_time: Time before taking the picture (default: 2 seconds)
        :type warmup_time: float

        :param resize: Set if you want to resize the picture to a new format
        :type resize: list or tuple (with two elements)

        :param opts: Extra options to pass to the camera (see
            https://www.raspberrypi.org/documentation/usage/camera/python/README.md)
        """

        if self._time_lapse_thread:
            return None, 'A time lapse thread is already running'

        camera = self._get_camera(**opts)
        directory = os.path.abspath(os.path.expanduser(directory))

        if warmup_time:
            time.sleep(warmup_time)

        capture_opts = {}
        if resize:
            capture_opts['resize'] = tuple(resize)

        def capture_thread():
            self.logger.info('Starting time lapse recording to directory {}'.format(directory))
            i = 0

            for filename in camera.capture_continuous(os.path.join(directory, 'image_{counter:04d}.jpg')):
                i += 1
                self.logger.debug('Captured {}'.format(filename))

                if i >= n_images:
                    break

                self._time_lapse_stop_condition.acquire()
                should_stop = self._time_lapse_stop_condition.wait(timeout=interval)
                self._time_lapse_stop_condition.release()

                if should_stop:
                    break

            self._time_lapse_thread = None
            self.logger.info('Stopped time lapse recording')

        self._time_lapse_thread = threading.Thread(target=capture_thread)
        self._time_lapse_thread.start()

    @action
    def stop_time_lapse(self):
        """
        Stop a time lapse sequence if it's running
        """

        if not self._time_lapse_thread:
            self.logger.info('No time lapse thread is running')
            return

        self._time_lapse_stop_condition.acquire()
        self._time_lapse_stop_condition.notify_all()
        self._time_lapse_stop_condition.release()

        if self._time_lapse_thread:
            self._time_lapse_thread.join()

    # noinspection PyMethodOverriding
    @action
    def start_recording(self, video_file=None, directory=None, name_format='video_%04d.h264', duration=None,
                        split_duration=None, **opts):
        """
        Start recording to a video file or to multiple video files

        :param video_file: Path of the video file, if you want to keep the recording all in one file
        :type video_file: str

        :param directory: Path of the directory that will store the video files, if you want to split the recording
            on multiple files. Note that you need to specify either video_file (to save the recording to one single
            file) or directory (to split the recording on multiple files)
        :type directory: str

        :param name_format: If you're splitting the recording to multiple files, then you can specify the name format
            for those files (default: 'video_%04d.h264')
            on multiple files. Note that you need to specify either video_file (to save the recording to one single
            file) or directory (to split the recording on multiple files)
        :type name_format: str

        :param duration: Video duration in seconds (default: None, record until stop_recording is called)
        :type duration: float

        :param split_duration: If you're splitting the recording to multiple files, then you should specify how long
            each video should be in seconds
        :type split_duration: float

        :param opts: Extra options to pass to the camera (see
            https://www.raspberrypi.org/documentation/usage/camera/python/README.md)
        """

        if self._recording_thread:
            return None, 'A recording thread is already running'

        multifile = not video_file
        if multifile and not (directory and split_duration):
            return None, 'No video_file specified for single file capture and no directory/split_duration specified for multifile split'

        camera = self._get_camera(**opts)
        video_file = os.path.abspath(os.path.expanduser(video_file))

        def recording_thread():
            if not multifile:
                self.logger.info('Starting recording to video file {}'.format(video_file))
                camera.start_recording(video_file)
                self._recording_stop_condition.acquire()
                self._recording_stop_condition.wait(timeout=duration)
                self._recording_stop_condition.release()
                self.logger.info('Video recorded to {}'.format(video_file))
            else:
                self.logger.info('Starting recording video files to directory {}'.format(directory))

                i = 1
                start_time = time.time()
                end_time = None
                if duration is not None:
                    end_time = time.time() + duration

                camera.start_recording(name_format % i)
                self._recording_stop_condition.acquire()
                self._recording_stop_condition.wait(timeout=split_duration)
                self._recording_stop_condition.release()
                self.logger.info('Video file {} saved'.format(name_format % i))

                while True:
                    i += 1
                    remaining_duration = None

                    if end_time:
                        remaining_duration = end_time - time.time()
                        split_duration = min(split_duration, remaining_duration)
                        if remaining_duration <= 0:
                            break

                    camera.split_recording(name_format % i)
                    self._recording_stop_condition.acquire()
                    should_stop = self._recording_stop_condition.wait(timeout=split_duration)
                    self._recording_stop_condition.release()
                    self.logger.info('Video file {} saved'.format(name_format % i))

                    if should_stop:
                        break

            self.camera.stop_recording()
            self._recording_thread = None

        self._recording_thread = threading.Thread(target=recording_thread)
        self._recording_thread.start()

    @action
    def stop_recording(self, **kwargs):
        """
        Stop a camera recording
        """

        if not self._recording_thread:
            self.logger.info('No recording thread is running')
            return

        self._recording_stop_condition.acquire()
        self._recording_stop_condition.notify_all()
        self._recording_stop_condition.release()

        if self._recording_thread:
            self._recording_thread.join()

    @action
    def start_streaming(self, listen_port=5000, duration=None, format='h264' **opts):
        """
        Start recording to a network stream

        :param listen_port: TCP listen port (default: 5000)
        :type listen_port: int

        :param duration: Stream duration in seconds (default: None, record until stop_streaming is called)
        :type duration: float

        :param format: Video stream format (default: h264)
        :type format: str

        :param opts: Extra options to pass to the camera (see
            https://www.raspberrypi.org/documentation/usage/camera/python/README.md)
        """

        if self._streaming_thread:
            return None, 'A streaming thread is already running'

        camera = self._get_camera(**opts)
        server_socket = socket.socket()
        server_socket.bind(('0.0.0.0', listen_port))
        server_socket.listen(0)

        def streaming_thread():
            self.logger.info('Starting streaming on listen port {}'.format(listen_port))

            while True:
                socket = server_socket.accept()[0].makefile('wb')
                self.logger.info('Accepted client connection from {}'.format(socket.getpeername()))

                try:
                    camera.start_recording(socket, format=format)
                    self._streaming_stop_condition.acquire()
                    self._streaming_stop_condition.wait(timeout=duration)
                    self._streaming_stop_condition.release()
                    break
                except ConnectionError:
                    self.logger.info('Client closed connection')

                    try:
                        socket.close()
                    except:
                        pass

            self.camera.stop_recording()
            self._streaming_thread = None
            self.logger.info('Stopped camera stream')

        self._streaming_thread = threading.Thread(target=streaming_thread)
        self._streaming_thread.start()

    @action
    def stop_streaming(self, **kwargs):
        """
        Stop a camera streaming session
        """

        if not self._streaming_thread:
            self.logger.info('No recording thread is running')
            return

        self._streaming_stop_condition.acquire()
        self._streaming_stop_condition.notify_all()
        self._streaming_stop_condition.release()

        if self._streaming_thread:
            self._streaming_thread.join()


# vim:sw=4:ts=4:et:
