import json
from typing import Optional

from flask import Blueprint, request
from flask.wrappers import Response

from platypush.backend.http.app import template_folder
from platypush.backend.http.app.utils import authenticate
from platypush.context import get_plugin
from platypush.plugins.camera import CameraPlugin, Camera, StreamWriter

camera = Blueprint('camera', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    camera,
]


def get_camera(plugin: str) -> CameraPlugin:
    plugin_name = f'camera.{plugin}'
    p = get_plugin(plugin_name)
    assert p, f'No such plugin: {plugin_name}'
    return p


def get_frame(session: Camera, timeout: Optional[float] = None) -> Optional[bytes]:
    if session.stream:
        with session.stream.ready:
            session.stream.ready.wait(timeout=timeout)
            return session.stream.frame


def feed(camera: CameraPlugin, **kwargs):
    with camera.open(**kwargs) as session:
        camera.start_camera(session)
        while True:
            frame = get_frame(session, timeout=5.0)
            if frame:
                yield frame


def get_args(kwargs):
    kwargs = kwargs.copy()
    if 't' in kwargs:
        del kwargs['t']

    for k, v in kwargs.items():
        if k == 'resolution':
            v = json.loads('[{}]'.format(v))
        else:
            try:
                v = int(v)
            except (ValueError, TypeError):
                try:
                    v = float(v)
                except (ValueError, TypeError):
                    pass

        kwargs[k] = v

    return kwargs


@camera.route('/camera/<plugin>/photo.<extension>', methods=['GET'])
@authenticate()
def get_photo(plugin, extension):
    plugin = get_camera(plugin)
    extension = 'jpeg' if extension in ('jpg', 'jpeg') else extension

    with plugin.open(stream=True, stream_format=extension, frames_dir=None, **get_args(request.args)) as session:
        plugin.start_camera(session)
        frame = None
        for _ in range(session.info.warmup_frames):
            frame = get_frame(session)

        return Response(frame, mimetype=session.stream.mimetype)


@camera.route('/camera/<plugin>/video.<extension>', methods=['GET'])
@authenticate()
def get_video(plugin, extension):
    stream_class = StreamWriter.get_class_by_name(extension)
    camera = get_camera(plugin)
    return Response(
        feed(camera, stream=True, stream_format=extension, frames_dir=None,
            **get_args(request.args)
        ), mimetype=stream_class.mimetype
    )


@camera.route('/camera/<plugin>/photo', methods=['GET'])
@authenticate()
def get_photo_default(plugin):
    return get_photo(plugin, 'jpeg')


@camera.route('/camera/<plugin>/video', methods=['GET'])
@authenticate()
def get_video_default(plugin):
    return get_video(plugin, 'mjpeg')


@camera.route('/camera/<plugin>/frame', methods=['GET'])
@authenticate()
def get_photo_deprecated(plugin):
    return get_photo_default(plugin)


@camera.route('/camera/<plugin>/feed', methods=['GET'])
@authenticate()
def get_video_deprecated(plugin):
    return get_video_default(plugin)


# vim:sw=4:ts=4:et:
