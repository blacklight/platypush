import os
import shutil
import tempfile
import time

from flask import Response, Blueprint, send_from_directory

from platypush.backend.http.app import template_folder
from platypush.backend.http.app.utils import authenticate, send_request

camera = Blueprint('camera', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    camera,
]


def get_device_id(device_id=None):
    if device_id is None:
        device_id = str(send_request(action='camera.get_default_device_id').output)
    return device_id


def get_frame_file(device_id=None):
    device_id = get_device_id(device_id)
    was_recording = True
    frame_file = None
    status = send_request(action='camera.status', device_id=device_id).output

    if device_id not in status:
        was_recording = False
        send_request(action='camera.start_recording',
                     device_id=device_id)

    while not frame_file:
        frame_file = send_request(action='camera.status', device_id=device_id). \
            output.get(device_id, {}).get('image_file')

        if not frame_file:
            time.sleep(0.1)

    if not was_recording:
        with tempfile.NamedTemporaryFile(prefix='camera_capture_', suffix='.jpg',
                                         delete=False) as f:
            # stop_recording will delete the temporary frames. Copy the image file
            # to a temporary file before stopping recording
            tmp_file = f.name

        shutil.copyfile(frame_file, tmp_file)
        frame_file = tmp_file
        send_request(action='camera.stop_recording', device_id=device_id)

    return frame_file


def video_feed(device_id=None):
    device_id = get_device_id(device_id)
    send_request(action='camera.start_recording', device_id=device_id)
    last_frame_file = None

    try:
        while True:
            frame_file = get_frame_file(device_id)
            if frame_file == last_frame_file:
                continue

            with open(frame_file, 'rb') as f:
                frame = f.read()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            last_frame_file = frame_file
    finally:
        send_request(action='camera.stop_recording', device_id=device_id)


@camera.route('/camera/<device_id>/frame', methods=['GET'])
@authenticate()
def get_camera_frame(device_id):
    frame_file = get_frame_file(device_id)
    return send_from_directory(os.path.dirname(frame_file),
                               os.path.basename(frame_file))


@camera.route('/camera/frame', methods=['GET'])
@authenticate()
def get_default_camera_frame():
    frame_file = get_frame_file()
    return send_from_directory(os.path.dirname(frame_file),
                               os.path.basename(frame_file))


@camera.route('/camera/stream', methods=['GET'])
@authenticate()
def get_default_stream_feed():
    return Response(video_feed(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@camera.route('/camera/<device_id>/stream', methods=['GET'])
@authenticate()
def get_stream_feed(device_id):
    return Response(video_feed(device_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# vim:sw=4:ts=4:et:
