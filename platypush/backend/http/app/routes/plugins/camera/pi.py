import os
import tempfile

from flask import Response, Blueprint, send_from_directory

from platypush.backend.http.app import template_folder
from platypush.backend.http.app.utils import authenticate, send_request

camera_pi = Blueprint('camera.pi', __name__, template_folder=template_folder)
filename = os.path.join(tempfile.gettempdir(), 'camera_pi.jpg')

# Declare routes list
__routes__ = [
    camera_pi,
]


def get_frame_file(*args, **kwargs):
    response = send_request(*args, action='camera.pi.take_picture', image_file=filename, **kwargs)
    assert response['output'] and 'image_file' in response['output'],\
        response['errors'].get(0, 'Unable to capture an image file')

    return response['output']['image_file']


def video_feed():
    try:
        while True:
            frame_file = get_frame_file(warmup_time=0, close=False)
            with open(frame_file, 'rb') as f:
                frame = f.read()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        send_request(action='camera.pi.close')


@camera_pi.route('/camera/pi/frame', methods=['GET'])
@authenticate()
def get_frame():
    frame_file = get_frame_file()
    return send_from_directory(os.path.dirname(frame_file),
                               os.path.basename(frame_file))


@camera_pi.route('/camera/pi/stream', methods=['GET'])
@authenticate()
def get_stream_feed():
    return Response(video_feed(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# vim:sw=4:ts=4:et:
