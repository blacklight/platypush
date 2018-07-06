import json
import socket
import time

from enum import Enum
from threading import Thread

from platypush.backend import Backend
from platypush.context import get_backend

class CameraPiBackend(Backend):
    """
    Backend to interact with a Raspberry Pi camera. It can start and stop
    recordings and take pictures. It can be programmatically controlled through
    the :class:`platypush.plugins.camera.pi` plugin. Note that the Redis backend
    must be configured and running to enable camera control.

    Requires:

        * **picamera** (``pip install picamera``)
        * **redis** (``pip install redis``) for inter-process communication with the camera process
    """

    class CameraAction(Enum):
        START_RECORDING = 'START_RECORDING'
        STOP_RECORDING = 'STOP_RECORDING'
        TAKE_PICTURE = 'TAKE_PICTURE'

        def __eq__(self, other):
            return self.value == other

    def __init__(self, listen_port, x_resolution=640, y_resolution=480,
                 redis_queue='platypush/camera/pi',
                 start_recording_on_startup=True,
                 framerate=24, hflip=False, vflip=False,
                 sharpness=0, contrast=0, brightness=50,
                 video_stabilization=False, ISO=0, exposure_compensation=0,
                 exposure_mode='auto', meter_mode='average', awb_mode='auto',
                 image_effect='none', color_effects=None, rotation=0,
                 crop=(0.0, 0.0, 1.0, 1.0), **kwargs):
        """
        See https://www.raspberrypi.org/documentation/usage/camera/python/README.md
        for a detailed reference about the Pi camera options.

        :param listen_port: Port where the camera process will provide the video output while recording
        :type listen_port: int
        """

        import picamera
        super().__init__(**kwargs)

        self.listen_port = listen_port
        self.server_socket = socket.socket()
        self.server_socket.bind(('0.0.0.0', self.listen_port))
        self.server_socket.listen(0)

        self.camera = picamera.PiCamera()
        self.camera.resolution = (x_resolution, y_resolution)
        self.camera.framerate = framerate
        self.camera.hflip = hflip
        self.camera.vflip = vflip
        self.camera.sharpness = sharpness
        self.camera.contrast = contrast
        self.camera.brightness = brightness
        self.camera.video_stabilization = video_stabilization
        self.camera.ISO = ISO
        self.camera.exposure_compensation = exposure_compensation
        self.camera.exposure_mode = exposure_mode
        self.camera.meter_mode = meter_mode
        self.camera.awb_mode = awb_mode
        self.camera.image_effect = image_effect
        self.camera.color_effects = color_effects
        self.camera.rotation = rotation
        self.camera.crop = crop
        self.start_recording_on_startup = start_recording_on_startup
        self.redis = None
        self.redis_queue = redis_queue
        self._recording_thread = None


    def send_camera_action(self, action, **kwargs):
        action = {
            'action': action.value,
            **kwargs
        }

        self.redis.send_message(msg=json.dumps(action), queue_name=self.redis_queue)

    def take_picture(self, image_file):
        """
        Take a picture.

        :param image_file: Output image file
        :type image_file: str
        """
        self.logger.info('Capturing camera snapshot to {}'.format(image_file))
        self.camera.capture(image_file)
        self.logger.info('Captured camera snapshot to {}'.format(image_file))

    def start_recording(self, video_file=None, format='h264'):
        """
        Start a recording.

        :param video_file: Output video file. If specified, the video will be recorded to file, otherwise it will be served via TCP/IP on the listen_port. Use ``stop_recording`` to stop the recording.
        :type video_file: str

        :param format: Video format (default: h264)
        :type format: str
        """

        def recording_thread():
            if video_file:
                self.camera.start_recording(video_file, format=format)
                while True:
                    self.camera.wait_recording(2)
            else:
                while True:
                    connection = self.server_socket.accept()[0].makefile('wb')
                    self.logger.info('Accepted client connection on port {}'.
                                    format(self.listen_port))

                    try:
                        self.camera.start_recording(connection, format=format)
                        while True:
                            self.camera.wait_recording(2)
                    except ConnectionError:
                        self.logger.info('Client closed connection')
                        try:
                            self.stop_recording()
                            connection.close()
                        except:
                            pass

                        self.send_camera_action(self.CameraAction.START_RECORDING)

            self._recording_thread = None

            try:
                self.camera.stop_recording()
            except:
                pass

        if self._recording_thread:
            self.logger.info('Recording already running')
            return

        self.logger.info('Starting camera recording')
        self._recording_thread = Thread(target=recording_thread)
        self._recording_thread.start()


    def stop_recording(self):
        """ Stops recording """

        self.logger.info('Stopping camera recording')

        try:
            self.camera.stop_recording()
        except Exception as e:
            self.logger.warning('Failed to stop recording')
            self.logger.exception(e)

    def run(self):
        super().run()

        if not self.redis:
            self.redis = get_backend('redis')

        if self.start_recording_on_startup:
            self.send_camera_action(self.CameraAction.START_RECORDING)

        self.logger.info('Initialized Pi camera backend')

        while not self.should_stop():
            try:
                msg = self.redis.get_message(self.redis_queue)

                if msg.get('action') == self.CameraAction.START_RECORDING:
                    self.start_recording()
                elif msg.get('action') == self.CameraAction.STOP_RECORDING:
                    self.stop_recording()
                elif msg.get('action') == self.CameraAction.TAKE_PICTURE:
                    self.take_picture(image_file=msg.get('image_file'))
            except Exception as e:
                self.logger.exception(e)


# vim:sw=4:ts=4:et:

