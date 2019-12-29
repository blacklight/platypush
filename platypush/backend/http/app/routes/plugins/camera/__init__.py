from flask import Response, Blueprint
from platypush.plugins.camera import CameraPlugin

from platypush import Config
from platypush.backend.http.app import template_folder
from platypush.backend.http.app.utils import authenticate, send_request

camera = Blueprint('camera', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    camera,
]


def get_device_id(device_id=None):
    if device_id is None:
        device_id = int(send_request(action='camera.get_default_device_id').output)
    return device_id


def get_camera(device_id=None):
    device_id = get_device_id(device_id)
    camera_conf = Config.get('camera') or {}
    camera_conf['device_id'] = device_id
    return CameraPlugin(**camera_conf)


def get_frame(device_id=None):
    cam = get_camera(device_id)
    with cam:
        frame = None

        for _ in range(cam.warmup_frames):
            output = cam.get_stream()

            with output.ready:
                output.ready.wait()
                frame = output.frame

        return frame


def video_feed(device_id=None):
    cam = get_camera(device_id)

    with cam:
        while True:
            output = cam.get_stream()
            with output.ready:
                output.ready.wait()
                frame = output.frame

            if frame and len(frame):
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@camera.route('/camera/<device_id>/frame', methods=['GET'])
@authenticate()
def get_camera_frame(device_id):
    frame = get_frame(device_id)
    return Response(frame, mimetype='image/jpeg')


@camera.route('/camera/frame', methods=['GET'])
@authenticate()
def get_default_camera_frame():
    frame = get_frame()
    return Response(frame, mimetype='image/jpeg')


@camera.route('/camera/<device_id>/stream', methods=['GET'])
@authenticate()
def get_stream_feed(device_id):
    return Response(video_feed(device_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@camera.route('/camera/stream', methods=['GET'])
@authenticate()
def get_default_stream_feed():
    return Response(video_feed(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# vim:sw=4:ts=4:et:
