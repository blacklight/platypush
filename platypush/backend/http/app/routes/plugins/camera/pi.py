import os
import tempfile

from flask import Response, Blueprint, send_from_directory
from typing import Optional

from platypush.backend.http.app import template_folder
from platypush.backend.http.app.utils import authenticate, send_request
from platypush.config import Config
from platypush.plugins.camera.pi import CameraPiPlugin

camera_pi = Blueprint('camera.pi', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    camera_pi,
]


def video_feed():
    camera: Optional[CameraPiPlugin] = None

    try:
        camera_conf = Config.get('camera.pi') or {}
        camera = CameraPiPlugin(**camera_conf)

        while True:
            output = camera.get_output_stream()
            with output.ready:
                output.ready.wait()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + output.frame + b'\r\n')
    finally:
        if camera:
            camera.close_output_stream()


@camera_pi.route('/camera/pi/frame', methods=['GET'])
@authenticate()
def get_frame_img():
    filename = os.path.join(tempfile.gettempdir(), 'camera_pi.jpg')
    response = send_request('camera.pi.take_picture', image_file=filename)
    frame_file = (response.output or {}).get('image_file')
    assert frame_file is not None

    return send_from_directory(os.path.dirname(frame_file),
                               os.path.basename(frame_file))


@camera_pi.route('/camera/pi/stream', methods=['GET'])
@authenticate()
def get_stream_feed():
    return Response(video_feed(),
                    headers={'Cache-Control': 'no-cache, private', 'Pragma': 'no-cache', 'Age': 0},
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# vim:sw=4:ts=4:et:
