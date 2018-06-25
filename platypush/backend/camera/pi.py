import json
import socket
import time

from enum import Enum
from redis import Redis
from threading import Thread

from platypush.backend import Backend

class CameraPiBackend(Backend):
    """
    Backend to interact with a Raspberry Pi camera. It can start and stop
    recordings and take pictures. It can be programmatically controlled through
    the :class:`platypush.plugins.camera.pi` plugin.

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
                 redis_queue='platypush_mq_camera',
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
        self.redis = Redis()
        self.redis_queue = redis_queue
        self._recording_thread = None

        if self.start_recording_on_startup:
            self.send_camera_action(self.CameraAction.START_RECORDING)

        self.logger.info('Initialized Pi camera backend')

    def send_camera_action(self, action, **kwargs):
        action = {
            'action': action.value,
            **kwargs
        }

        self.redis.rpush(self.redis_queue, json.dumps(action))

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
                    self.camera.wait_recording(60)
            else:
                connection = self.server_socket.accept()[0].makefile('wb')
                self.logger.info('Accepted client connection on port {}'.
                                format(self.listen_port))

                try:
                    self.camera.start_recording(connection, format=format)
                    while True:
                        self.camera.wait_recording(60)
                except ConnectionError:
                    self.logger.info('Client closed connection')
                    try:
                        self.stop_recording()
                        connection.close()
                    except:
                        pass

                    self.send_camera_action(self.CameraAction.START_RECORDING)

            self._recording_thread = None

        if self._recording_thread:
            self._recording_thread.join()

        self.logger.info('Starting camera recording')
        self._recording_thread = Thread(target=recording_thread)
        self._recording_thread.start()


    def stop_recording(self):
        """ Stops recording """

        self.logger.info('Stopping camera recording')

        try:
            self.camera.stop_recording()
        except:
            self.logger.info('No recording currently in progress')

    def run(self):
        super().run()

        while not self.should_stop():
            msg = json.loads(self.redis.blpop(self.redis_queue)[1].decode())

            if msg.get('action') == self.CameraAction.START_RECORDING:
                self.start_recording()
            elif msg.get('action') == self.CameraAction.STOP_RECORDING:
                self.stop_recording()
            elif msg.get('action') == self.CameraAction.TAKE_PICTURE:
                self.take_picture(image_file=msg.get('image_file'))


# vim:sw=4:ts=4:et:

