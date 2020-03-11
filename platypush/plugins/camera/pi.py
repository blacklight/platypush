"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
"""

import os
import socket
import threading
import time

from typing import Optional

from platypush.plugins import action
from platypush.plugins.camera import CameraPlugin, StreamingOutput


class CameraPiPlugin(CameraPlugin):
    """
    Plugin to control a Pi camera.

    Requires:

        * **picamera** (``pip install picamera``)
        * **numpy** (``pip install numpy``)

    """

    _default_resolution = (800, 600)
    _default_listen_port = 5000

    def __init__(self, resolution=(_default_resolution[0], _default_resolution[1]), framerate=24,
                 hflip=False, vflip=False, sharpness=0, contrast=0, brightness=50, video_stabilization=False, iso=0,
                 exposure_compensation=0, exposure_mode='auto', meter_mode='average', awb_mode='auto',
                 image_effect='none', color_effects=None, rotation=0, crop=(0.0, 0.0, 1.0, 1.0),
                 listen_port: int = _default_listen_port, **kwargs):
        """
        See https://www.raspberrypi.org/documentation/usage/camera/python/README.md
        for a detailed reference about the Pi camera options.

        :param listen_port: Default port that will be used for streaming the feed (default: 5000)
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
        self.listen_port = listen_port

        self._time_lapse_thread = None
        self._recording_thread = None
        self._streaming_thread = None
        self._capturing_thread = None
        self._time_lapse_stop_condition = threading.Condition()
        self._recording_stop_condition = threading.Condition()
        self._can_stream = False
        self._can_capture = False

    # noinspection PyUnresolvedReferences,PyPackageRequirements
    def _get_camera(self, **opts):
        if self._camera and not self._camera.closed:
            return self._camera

        import picamera
        self._camera = picamera.PiCamera()

        for (attr, value) in self.camera_args.items():
            setattr(self._camera, attr, value)
        for (attr, value) in opts.items():
            setattr(self._camera, attr, value)

        return self._camera

    @action
    def close(self):
        """
        Close an active connection to the camera.
        """
        import picamera

        if self._output and self._camera:
            try:
                self._camera.stop_recording()
            except picamera.PiCameraNotRecording:
                pass

        if self._camera and not self._camera.closed:
            try:
                self._camera.close()
            except picamera.PiCameraClosed:
                pass

        self._camera = None

    @action
    def start_preview(self, **opts):
        """
        Start camera preview.

        :param opts: Extra options to pass to the camera (see
            https://www.raspberrypi.org/documentation/usage/camera/python/README.md)
        """
        camera = self._get_camera(**opts)
        camera.start_preview()

    @action
    def stop_preview(self):
        """
        Stop camera preview.
        """
        camera = self._get_camera()
        try:
            camera.stop_preview()
        except Exception as e:
            self.logger.warning(str(e))

    @action
    def take_picture(self, image_file, preview=False, warmup_time=2, resize=None, close=True, **opts):
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

        :param close: If True (default) close the connection to the camera after capturing,
            otherwise keep the connection open (e.g. if you want to take a sequence of pictures).
            If you set close=False you should remember to call ``close`` when you don't need
            the connection anymore.

        :return: dict::

            {"image_file": path_to_the_image}

        """

        camera = None

        try:
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

            if preview:
                camera.stop_preview()

            return {'image_file': image_file}
        finally:
            if camera and close:
                self.close()

    def _raw_capture(self):
        import numpy as np
        resolution = self.camera_args['resolution']
        camera = self._get_camera()

        while self._can_capture:
            shape = (resolution[1] + (resolution[1]%16),
                     resolution[0] + (resolution[0]%32),
                     3)

            frame = np.empty(shape, dtype=np.uint8)
            camera.capture(frame, 'bgr')
            frame.reshape((shape[0], shape[1], 3))
            self._output.write(frame)

    def __enter__(self):
        camera = self._get_camera()
        self._output = StreamingOutput(raw=self.stream_raw_frames)
        self._can_capture = True

        if self.stream_raw_frames:
            self._capturing_thread = threading.Thread(target=self._raw_capture)
            self._capturing_thread.start()
        else:
            camera.start_recording(self._output, format='mjpeg')

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._can_capture = False
        if self._capturing_thread:
            self._capturing_thread.join()
            self._capturing_thread = None

        self.close()

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

        try:
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

            images = [os.path.join(directory, name_format % (i+1)) for i in range(0, n_images)]
            camera.capture_sequence(images, **capture_opts)

            if preview:
                camera.stop_preview()

            return {'image_files': images}
        finally:
            self.close()

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
            try:
                self.logger.info('Starting time lapse recording to directory {}'.format(directory))
                i = 0

                for filename in camera.capture_continuous(os.path.join(directory, 'image_{counter:04d}.jpg')):
                    i += 1
                    self.logger.info('Captured {}'.format(filename))

                    if n_images and i >= n_images:
                        break

                    self._time_lapse_stop_condition.acquire()
                    should_stop = self._time_lapse_stop_condition.wait(timeout=interval)
                    self._time_lapse_stop_condition.release()

                    if should_stop:
                        break
            finally:
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
            return None, 'No video_file specified for single file capture and no directory/split_duration ' + \
                   'specified for multi-file split'

        camera = self._get_camera(**opts)
        video_file = os.path.abspath(os.path.expanduser(video_file))

        def recording_thread():
            try:
                if not multifile:
                    self.logger.info('Starting recording to video file {}'.format(video_file))
                    camera.start_recording(video_file, format='h264')
                    self._recording_stop_condition.acquire()
                    self._recording_stop_condition.wait(timeout=duration)
                    self._recording_stop_condition.release()
                    self.logger.info('Video recorded to {}'.format(video_file))
                    return

                self.logger.info('Starting recording video files to directory {}'.format(directory))
                i = 1
                end_time = None
                timeout = split_duration

                if duration is not None:
                    end_time = time.time() + duration
                    timeout = min(split_duration, duration)

                camera.start_recording(name_format % i, format='h264')
                self._recording_stop_condition.acquire()
                self._recording_stop_condition.wait(timeout=timeout)
                self._recording_stop_condition.release()
                self.logger.info('Video file {} saved'.format(name_format % i))

                while True:
                    i += 1
                    timeout = None

                    if end_time:
                        remaining_duration = end_time - time.time()
                        timeout = min(split_duration, remaining_duration)
                        if remaining_duration <= 0:
                            break

                    camera.split_recording(name_format % i)
                    self._recording_stop_condition.acquire()
                    should_stop = self._recording_stop_condition.wait(timeout=timeout)
                    self._recording_stop_condition.release()
                    self.logger.info('Video file {} saved'.format(name_format % i))

                    if should_stop:
                        break
            finally:
                try:
                    camera.stop_recording()
                except Exception as e:
                    self.logger.exception(e)

                self._recording_thread = None
                self.logger.info('Stopped camera recording')

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

    # noinspection PyShadowingBuiltins
    @action
    def start_streaming(self, listen_port: Optional[int] = None, format='h264', **opts):
        """
        Start recording to a network stream

        :param listen_port: TCP listen port (default: `listen_port` configured value or 5000)
        :type listen_port: int

        :param format: Video stream format (default: h264)
        :type format: str

        :param opts: Extra options to pass to the camera (see
            https://www.raspberrypi.org/documentation/usage/camera/python/README.md)
        """

        if self._streaming_thread:
            return None, 'A streaming thread is already running'

        if not listen_port:
            listen_port = self.listen_port

        camera = self._get_camera(**opts)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', listen_port))
        server_socket.listen(1)
        server_socket.settimeout(1)

        # noinspection PyBroadException
        def streaming_thread():
            try:
                self.logger.info('Starting streaming on port {}'.format(listen_port))

                while self._can_stream:
                    try:
                        sock = server_socket.accept()[0]
                        stream = sock.makefile('wb')
                        self.logger.info('Accepted client connection from {}'.format(sock.getpeername()))
                    except socket.timeout:
                        continue

                    try:
                        if stream:
                            camera.start_recording(stream, format=format)
                            while True:
                                camera.wait_recording(1)
                    except ConnectionError:
                        self.logger.info('Client closed connection')
                    finally:
                        if sock:
                            sock.close()
            finally:
                try:
                    server_socket.close()
                    camera.stop_recording()
                except:
                    pass

                try:
                    camera.close()
                except:
                    pass

                self._streaming_thread = None
                self.logger.info('Stopped camera stream')

        self._can_stream = True
        self._streaming_thread = threading.Thread(target=streaming_thread)
        self._streaming_thread.start()

    @action
    def stop_streaming(self):
        """
        Stop a camera streaming session
        """

        if not self._streaming_thread:
            self.logger.info('No recording thread is running')
            return

        self._can_stream = False

        if self._streaming_thread:
            self._streaming_thread.join()

    @action
    def is_streaming(self):
        """
        :return: True if the Pi Camera network streaming thread is running,
            False otherwise.
        """
        return self._streaming_thread is not None


# vim:sw=4:ts=4:et:
