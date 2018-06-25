"""
.. moduleauthor:: Fabio Manganiello <blacklight86@gmail.com>
"""

from platypush.context import get_backend
from platypush.message.response import Response

from platypush.plugins import Plugin


class CameraPiPlugin(Plugin):
    """
    Plugin to control a Pi camera.
    It acts as a wrapper around the :mod:`platypush.backend.camera.pi` backend
    to programmatically control the status.
    """

    def start_recording(self):
        """
        Start recording
        """
        camera = get_backend('camera.pi')
        camera.send_camera_action(camera.CameraAction.START_RECORDING)
        return Response(output={'status':'ok'})

    def stop_recording(self):
        """
        Stop recording
        """
        camera = get_backend('camera.pi')
        camera.send_camera_action(camera.CameraAction.STOP_RECORDING)
        return Response(output={'status':'ok'})

    def take_picture(self, image_file):
        """
        Take a picture.

        :param image_file: Path where the output image will be stored.
        :type image_file: str
        """
        camera = get_backend('camera.pi')
        camera.send_camera_action(camera.CameraAction.TAKE_PICTURE, image_file=image_file)
        return Response(output={'image_file':image_file})


# vim:sw=4:ts=4:et:

