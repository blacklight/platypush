from platypush.common.gstreamer import Pipeline
from platypush.plugins.camera import CameraInfo, Camera


class GStreamerCamera(Camera):
    info: CameraInfo
    object: Pipeline


# vim:sw=4:ts=4:et:
