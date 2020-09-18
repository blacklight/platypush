import io
from abc import ABC

from PIL.Image import Image

from platypush.plugins.camera.model.writer import StreamWriter


class ImageStreamWriter(StreamWriter, ABC):
    """
    Write camera frames to a stream as single JPEG items.
    """

    @staticmethod
    def _encode(image: Image, encoding: str, **kwargs) -> bytes:
        with io.BytesIO() as buf:
            image.save(buf, format=encoding, **kwargs)
            return buf.getvalue()


class JPEGStreamWriter(ImageStreamWriter):
    """
    Write camera frames to a stream as single JPEG items.
    """
    mimetype = 'image/jpeg'

    def __init__(self, *args, quality: int = 90, **kwargs):
        super().__init__(*args, **kwargs)
        assert 0 < quality <= 100, 'JPEG quality should be between 0 and 100'
        self.quality = quality

    def encode(self, image: Image) -> bytes:
        return self._encode(image, 'jpeg', quality=self.quality)


class PNGStreamWriter(ImageStreamWriter):
    """
    Write camera frames to a stream as single PNG items.
    """
    mimetype = 'image/png'

    def encode(self, image: Image) -> bytes:
        return self._encode(image, 'png')


class BMPStreamWriter(ImageStreamWriter):
    """
    Write camera frames to a stream as single BMP items.
    """
    mimetype = 'image/bmp'

    def encode(self, image: Image) -> bytes:
        return self._encode(image, 'bmp')


class MJPEGStreamWriter(JPEGStreamWriter):
    """
    Write camera frames to a stream as an MJPEG feed.
    """
    mimetype = 'multipart/x-mixed-replace; boundary=frame'

    def encode(self, image: Image) -> bytes:
        return (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + super().encode(image) + b'\r\n')


# vim:sw=4:ts=4:et:
