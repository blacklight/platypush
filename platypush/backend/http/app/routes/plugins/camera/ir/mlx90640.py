import base64
import os
import tempfile

from flask import Response, request, Blueprint, send_from_directory

from platypush.backend.http.app import template_folder
from platypush.backend.http.app.utils import authenticate, send_request

camera_ir_mlx90640 = Blueprint('camera.ir.mlx90640', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    camera_ir_mlx90640,
]


def get_feed(**args):
    try:
        while True:
            frame = send_request(action='camera.ir.mlx90640.capture', **args).output[0]
            frame = base64.decodebytes(frame.encode())
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        send_request(action='camera.ir.mlx90640.stop')


@camera_ir_mlx90640.route('/camera/ir/mlx90640/frame', methods=['GET'])
@authenticate()
def get_frame_route():
    f = tempfile.NamedTemporaryFile(prefix='ir_camera_frame_', suffix='.jpg', delete=False)
    args = {
        'grayscale': bool(int(request.args.get('grayscale', 0))),
        'scale_factor': int(request.args.get('scale_factor', 1)),
        'rotate': int(request.args.get('rotate', 0)),
        'output_file': f.name,
    }

    send_request(action='camera.ir.mlx90640.capture', **args)
    return send_from_directory(os.path.dirname(f.name),
                               os.path.basename(f.name))


@camera_ir_mlx90640.route('/camera/ir/mlx90640/stream', methods=['GET'])
@authenticate()
def get_feed_route():
    args = {
        'grayscale': bool(int(request.args.get('grayscale', 0))),
        'scale_factor': int(request.args.get('scale_factor', 1)),
        'rotate': int(request.args.get('rotate', 0)),
        'format': 'jpeg',
    }

    return Response(get_feed(**args),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# vim:sw=4:ts=4:et:
