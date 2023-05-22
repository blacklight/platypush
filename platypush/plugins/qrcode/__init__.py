import base64
import io
import os
import threading
import time
from typing import Optional, List

from platypush import Config
from platypush.context import get_bus
from platypush.message.event.qrcode import QrcodeScannedEvent
from platypush.message.response.qrcode import (
    QrcodeGeneratedResponse,
    QrcodeDecodedResponse,
    ResultModel,
)
from platypush.plugins import Plugin, action
from platypush.plugins.camera import CameraPlugin
from platypush.utils import get_plugin_class_by_name


class QrcodePlugin(Plugin):
    """
    Plugin to generate and scan QR and bar codes.

    Requires:

        * **numpy** (``pip install numpy``).
        * **qrcode** (``pip install 'qrcode[pil]'``) for QR generation.
        * **pyzbar** (``pip install pyzbar``) for decoding code from images.
        * **Pillow** (``pip install Pillow``) for image management.

    """

    def __init__(self, camera_plugin: Optional[str] = None, **kwargs):
        """
        :param camera_plugin: Name of the plugin that will be used as a camera to capture images (e.g.
            ``camera.cv`` or ``camera.pi``).
        """
        super().__init__(**kwargs)
        self.camera_plugin = camera_plugin
        self._capturing = threading.Event()

    def _get_camera(
        self, camera_plugin: Optional[str] = None, **config
    ) -> CameraPlugin:
        camera_plugin = camera_plugin or self.camera_plugin
        if not config:
            config = Config.get(camera_plugin) or {}
        config['stream_raw_frames'] = True

        cls = get_plugin_class_by_name(camera_plugin)
        assert cls and issubclass(
            cls, CameraPlugin
        ), '{} is not a valid camera plugin'.format(camera_plugin)
        return cls(**config)

    @action
    def generate(
        self,
        content: str,
        output_file: Optional[str] = None,
        show: bool = False,
        format: str = 'png',
    ) -> QrcodeGeneratedResponse:
        """
        Generate a QR code.
        If you configured the :class:`platypush.backend.http.HttpBackend` then you can also generate
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

    @staticmethod
    def _convert_frame(frame):
        import numpy as np
        from PIL import Image

        assert isinstance(
            frame, np.ndarray
        ), 'Image conversion only works with numpy arrays for now (got {})'.format(
            type(frame)
        )
        mode = 'RGB'
        if len(frame.shape) > 2 and frame.shape[2] == 4:
            mode = 'RGBA'

        return Image.frombuffer(
            mode, (frame.shape[1], frame.shape[0]), frame, 'raw', mode, 0, 1
        )

    @action
    def start_scanning(
        self,
        camera_plugin: Optional[str] = None,
        duration: Optional[float] = None,
        n_codes: Optional[int] = None,
    ) -> Optional[List[ResultModel]]:
        """
        Decode QR-codes and bar codes using a camera.

        Triggers:

            - :class:`platypush.message.event.qrcode.QrcodeScannedEvent` when a code is successfully scanned.

        :param camera_plugin: Camera plugin (overrides default ``camera_plugin``).
        :param duration: How long the capturing phase should run (default: until ``stop_scanning`` or app termination).
        :param n_codes: Stop after decoding this number of codes (default: None).
        :return: When ``duration`` or ``n_codes`` are specified or ``stop_scanning`` is called, it will return a list of
            :class:`platypush.message.response.qrcode.ResultModel` instances with the scanned results,
        """
        from pyzbar import pyzbar

        assert not self._capturing.is_set(), 'A capturing process is already running'

        camera = self._get_camera(camera_plugin)
        codes = []
        last_results = {}
        last_results_timeout = 10.0
        last_results_time = 0
        self._capturing.set()

        try:
            with camera:
                start_time = time.time()

                while (
                    self._capturing.is_set()
                    and (not duration or time.time() < start_time + duration)
                    and (not n_codes or len(codes) < n_codes)
                ):
                    output = camera.get_stream()
                    with output.ready:
                        output.ready.wait()
                        img = self._convert_frame(output.raw_frame)
                        results = pyzbar.decode(img)
                        if results:
                            results = [
                                result
                                for result in QrcodeDecodedResponse(results).output[
                                    'results'
                                ]
                                if result['data'] not in last_results
                                or time.time()
                                >= last_results_time + last_results_timeout
                            ]

                        if results:
                            codes.extend(results)
                            get_bus().post(QrcodeScannedEvent(results=results))
                            last_results = {
                                result['data']: result for result in results
                            }
                            last_results_time = time.time()
        finally:
            self._capturing.clear()

        return codes

    @action
    def stop_scanning(self):
        self._capturing.clear()


# vim:sw=4:ts=4:et:
