from enum import Enum

from platypush.plugins.camera.model.writer.ffmpeg import MKVStreamWriter, H264StreamWriter, H265StreamWriter
from platypush.plugins.camera.model.writer.image import JPEGStreamWriter, PNGStreamWriter, BMPStreamWriter, \
    MJPEGStreamWriter


class StreamHandlers(Enum):
    JPG = JPEGStreamWriter
    JPEG = JPEGStreamWriter
    PNG = PNGStreamWriter
    BMP = BMPStreamWriter
    MJPEG = MJPEGStreamWriter
    MJPG = MJPEGStreamWriter
    MKV = MKVStreamWriter
    WEBM = MKVStreamWriter
    H264 = H264StreamWriter
    H265 = H265StreamWriter
    MP4 = H264StreamWriter


# vim:sw=4:ts=4:et:
