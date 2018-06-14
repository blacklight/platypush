import socket
import time
import picamera

from threading import Event

from platypush.backend import Backend

class CameraPiBackend(Backend):
    def __init__(self, listen_port, x_resolution=640, y_resolution=480,
                 framerate=24, hflip=False, vflip=False,
                 sharpness=0, contrast=0, brightness=50,
                 video_stabilization=False, ISO=0, exposure_compensation=0,
                 exposure_mode='auto', meter_mode='average', awb_mode='auto',
                 image_effect='none', color_effects=None, rotation=0,
                 crop=(0.0, 0.0, 1.0, 1.0), **kwargs):
        """ See https://www.raspberrypi.org/documentation/usage/camera/python/README.md
            for a detailed reference about the Pi camera options """

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

        self.logger.info('Initialized Pi camera backend')

    def take_picture(self, image_file):
        self.logger.info('Capturing camera snapshot to {}'.format(image_file))
        self.camera.capture(image_file)
        self.logger.info('Captured camera snapshot to {}'.format(image_file))

    def start_recording(self, video_file=None, format='h264'):
        self.logger.info('Starting camera recording')

        if video_file:
            self.camera.start_recording(videofile, format=format)
        else:
            connection = self.server_socket.accept()[0].makefile('wb')
            self.logger.info('Accepted client connection on port {}'.
                             format(self.listen_port))

            self.camera.start_recording(connection, format=format)

    def stop_recording(self):
        self.logger.info('Stopping camera recording')

        try:
            self.camera.stop_recording()
        except:
            self.logger.info('No recording currently in progress')

    def run(self):
        super().run()

        while True:
            restart = True

            try:
                self.start_recording()
                while True:
                    self.camera.wait_recording(60)
            except ConnectionError:
                self.logger.info('Client closed connection')
            finally:
                try:
                    self.stop_recording()
                except Exception as e:
                    self.logger.exception(e)


# vim:sw=4:ts=4:et:

