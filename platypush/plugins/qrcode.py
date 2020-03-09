import base64
import io
import os
from typing import Optional

from platypush.message.response.qrcode import QrcodeGeneratedResponse, QrcodeDecodedResponse
from platypush.plugins import Plugin, action


class QrcodePlugin(Plugin):
    """
    Plugin to generate and scan QR and bar codes.

    Requires:

        * **qrcode** (``pip install 'qrcode[pil]'``) for QR generation.
        * **pyzbar** (``pip install pyzbar``) for decoding code from images.
        * **Pillow** (``pip install Pillow``) for image management.

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # noinspection PyShadowingBuiltins
    @action
    def generate(self, content: str, output_file: Optional[str] = None, show: bool = False,
                 format: str = 'png') -> QrcodeGeneratedResponse:
        """
        Generate a QR code.
        If you configured the :class`:platypush.backend.http.HttpBackend` then you can also generate
        codes directly from the browser through ``http://<host>:<port>/qrcode?content=...``.

        :param content: Text, URL or content of the QR code.
        :param output_file: If set then the QR code will be exported in the specified image file.
            Otherwise, a base64-encoded representation of its binary content will be returned in
            the response as ``data``.
        :param show: If True, and if the device where the application runs has an active display,
            then the generated QR code will be shown on display.
        :param format: Output image format (default: ``png``).
        :return: :class:`platypush.message.response.qrcode.QrcodeGeneratedResponse`.
        """
        import qrcode
        qr = qrcode.make(content)
        img = qr.get_image()
        ret = {
            'content': content,
            'format': format,
        }

        if show:
            img.show()
        if output_file:
            output_file = os.path.abspath(os.path.expanduser(output_file))
            img.save(output_file, format=format)
            ret['image_file'] = output_file
        else:
            f = io.BytesIO()
            img.save(f, format=format)
            ret['data'] = base64.encodebytes(f.getvalue()).decode()

        return QrcodeGeneratedResponse(**ret)

    @action
    def decode(self, image_file: str) -> QrcodeDecodedResponse:
        """
        Decode a QR code from an image file.

        :param image_file: Path of the image file.
        """
        from pyzbar import pyzbar
        from PIL import Image

        image_file = os.path.abspath(os.path.expanduser(image_file))
        img = Image.open(image_file)
        results = pyzbar.decode(img)
        return QrcodeDecodedResponse(results)


# vim:sw=4:ts=4:et:
