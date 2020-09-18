from flask import Blueprint

from platypush.backend.http.app import template_folder
from platypush.backend.http.app.routes.plugins.camera import get_photo, get_video
from platypush.backend.http.app.utils import authenticate

camera_ir_mlx90640 = Blueprint('camera.ir.mlx90640', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    camera_ir_mlx90640,
]


@camera_ir_mlx90640.route('/camera/ir/mlx90640/photo.<extension>', methods=['GET'])
@authenticate()
def get_photo_route(extension):
    return get_photo('ir.mlx90640', extension)


@camera_ir_mlx90640.route('/camera/ir/mlx90640/video.<extension>', methods=['GET'])
@authenticate()
def get_video_route(extension):
    return get_video('ir.mlx90640', extension)


@camera_ir_mlx90640.route('/camera/ir/mlx90640/photo', methods=['GET'])
@authenticate()
def get_photo_route_default():
    return get_photo_route('jpeg')


@camera_ir_mlx90640.route('/camera/ir/mlx90640/video', methods=['GET'])
@authenticate()
def get_video_route_default():
    return get_video_route('mjpeg')


@camera_ir_mlx90640.route('/camera/ir/mlx90640/frame', methods=['GET'])
@authenticate()
def get_photo_route_deprecated():
    return get_photo_route_default()


@camera_ir_mlx90640.route('/camera/ir/mlx90640/feed', methods=['GET'])
@authenticate()
def get_video_route_deprecated():
    return get_video_route_default()


# vim:sw=4:ts=4:et:
