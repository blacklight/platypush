import os
import tempfile

from flask import Response, Blueprint, send_from_directory
from typing import Optional

from platypush.backend.http.app import template_folder
from platypush.backend.http.app.utils import authenticate, send_request
from platypush.config import Config
from platypush.plugins.camera.pi import CameraPiPlugin

camera_pi = Blueprint('camera.pi', __name__, template_folder=template_folder)
filename = os.path.join(tempfile.gettempdir(), 'camera_pi.jpg')

# Declare routes list
__routes__ = [
    camera_pi,
]

_camera: Optional[CameraPiPlugin] = None


def get_camera() -> CameraPiPlugin:
    global _camera

    # noinspection PyProtectedMember
    if _camera and _camera._camera and not _camera._camera.closed:
        return _camera

    camera_conf = Config.get('camera.pi') or {}
    _camera = CameraPiPlugin(**camera_conf)
    return _camera


def get_frame():
    camera = get_camera()
    output = camera.get_output_stream()

    with output.ready:
        output.ready.wait()
        return output.frame


def video_feed():
    try:
        while True:
            frame = get_frame()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        send_request(action='camera.pi.close')


@camera_pi.route('/camera/pi/frame', methods=['GET'])
@authenticate()
def get_frame_img():
    response = send_request('camera.pi.take_picture', image_file=filename)
    frame_file = (response.output or {}).get('image_file')
    assert frame_file is not None

    return send_from_directory(os.path.dirname(frame_file),
                               os.path.basename(frame_file))


@camera_pi.route('/camera/pi/stream', methods=['GET'])
@authenticate()
def get_stream_feed():
    global _camera

    try:
        return Response(video_feed(),
                        headers={'Cache-Control': 'no-cache, private', 'Pragma': 'no-cache', 'Age': 0},
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    finally:
        if _camera:
            _camera.close_output_stream()
            _camera = None


# vim:sw=4:ts=4:et:
