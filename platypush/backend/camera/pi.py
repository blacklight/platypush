import logging
import socket
import time
import picamera

from platypush.backend import Backend

class CameraPiBackend(Backend):
    def __init__(self, listen_port, x_resolution=640, y_resolution=480,
                 framerate=24, hflip=False, vflip=False, **kwargs):
        super().__init__(**kwargs)

        self.listen_port = listen_port
        self.x_resolution = x_resolution
        self.y_resolution = y_resolution
        self.framerate = framerate
        self.hflip = hflip
        self.vflip = vflip

        self.server_socket = socket.socket()
        self.server_socket.bind(('0.0.0.0', self.listen_port))
        self.server_socket.listen(0)

        self.camera = picamera.PiCamera()
        self.camera.resolution = (self.x_resolution, self.y_resolution)
        self.camera.framerate = framerate
        self.camera.hflip = self.hflip
        self.camera.vflip = self.vflip

        logging.info('Initialized Pi camera backend')

    def send_message(self, msg):
        pass

    def run(self):
        super().run()

        while True:
            connection = self.server_socket.accept()[0].makefile('wb')

            try:
                self.camera.start_recording(connection, format='h264')
                while True:
                    self.camera.wait_recording(60)
            except ConnectionError as e:
                pass
            finally:
                try:
                    self.camera.stop_recording()
                    connection.close()
                except:
                    pass


# vim:sw=4:ts=4:et:

