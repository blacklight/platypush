import base64
import io
import os
import threading
import time
from typing import Optional, List, Union

import qrcode
from pyzbar import pyzbar
from PIL import Image

from platypush import Config
from platypush.context import get_bus
from platypush.message.event.qrcode import QrcodeScannedEvent
from platypush.plugins import Plugin, action
from platypush.plugins.camera import CameraPlugin
from platypush.schemas.qrcode import (
    QrcodeDecodedSchema,
    QrcodeDecodedResultSchema,
    QrcodeGeneratedSchema,
)
from platypush.utils import get_plugin_class_by_name


class QrcodePlugin(Plugin):
    """
    Plugin to generate and scan QR and bar codes.
    """

    def __init__(self, camera_plugin: Optional[str] = None, **kwargs):
        """
        :param camera_plugin: Name of the plugin that will be used as a camera
            to capture images (e.g. ``camera.cv`` or ``camera.pi``). This is
            required if you want to use the ``start_scanning`` action to scan
            QR codes from a camera.
        """
        super().__init__(**kwargs)
        self.camera_plugin = camera_plugin
        self._capturing = threading.Event()

    def _get_camera(
        self, camera_plugin: Optional[str] = None, **config
    ) -> CameraPlugin:
        camera_plugin = camera_plugin or self.camera_plugin
        assert camera_plugin, 'No camera plugin specified'
        if not config:
            config = Config.get(camera_plugin) or {}
        config['stream_raw_frames'] = True

        cls = get_plugin_class_by_name(camera_plugin)
        assert cls and issubclass(
            cls, CameraPlugin
        ), f'{camera_plugin} is not a valid camera plugin'
        return cls(**config)

    @action
    def generate(
        self,
        content: Union[str, bytes],
        binary: bool = False,
        output_file: Optional[str] = None,
        show: bool = False,
        format: str = 'png',
    ) -> dict:
        """
        Generate a QR code.

        If you configured the :class:`platypush.backend.http.HttpBackend` then
        you can also generate codes directly from the browser through
        ``http://<host>:<port>/qrcode?content=...``.

        :param content: Text, URL or content of the QR code.
        :param binary: If True then the content will be treated as binary data.
            Content needs to be either a bytes object or a base64-encoded
            string.
        :param output_file: If set then the QR code will be exported in the
            specified image file. Otherwise, a base64-encoded representation of
            its binary content will be returned in the response as ``data``.
        :param show: If True, and if the device where the application runs has
            an active display, then the generated QR code will be shown on
            display.
        :param format: Output image format (default: ``png``).
        :return: .. schema:: qrcode.QrcodeGeneratedSchema
        """
        if binary:
            if isinstance(content, str):
                try:
                    content = base64.b64decode(content)
                except ValueError as e:
                    raise AssertionError(f'Invalid base64-encoded binary content: {e}')

            assert isinstance(content, bytes), 'Invalid binary content'

        qr = qrcode.make(content)
        img = qr.get_image()
        ret = {
            'content': (
                content
                if isinstance(content, str)
                else base64.b64encode(content).decode()
            ),
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
            ret['data'] = base64.b64encode(f.getvalue()).decode()

        return dict(QrcodeGeneratedSchema().dump(ret))

    @action
    def decode(self, image_file: str) -> dict:
        """
        Decode a QR code from an image file.

        :param image_file: Path of the image file.
        :return: .. schema:: qrcode.QrcodeDecodedSchema
        """
        image_file = os.path.abspath(os.path.expanduser(image_file))
        with open(image_file, 'rb') as f:
            img = Image.open(f)
            results = pyzbar.decode(img)
            return dict(
                QrcodeDecodedSchema().dump(
                    {
                        'results': results,
                        'image_file': image_file,
                    }
                )
            )

    @action
    def start_scanning(
        self,
        camera_plugin: Optional[str] = None,
        duration: Optional[float] = None,
        n_codes: Optional[int] = None,
    ) -> Optional[List[dict]]:
        """
        Decode QR-codes and bar codes using a camera.

        :param camera_plugin: Camera plugin (overrides default ``camera_plugin``).
        :param duration: How long the capturing phase should run (default:
            until ``stop_scanning`` or app termination).
        :param n_codes: Stop after decoding this number of codes (default: None).
        :return: .. schema:: qrcode.QrcodeDecodedResultSchema(many=True)
        """
        assert not self._capturing.is_set(), 'A capturing process is already running'

        camera = self._get_camera(camera_plugin)
        codes = []
        last_results = {}
        last_results_timeout = 5.0
        last_results_time = 0
        self._capturing.set()

        try:
            with camera.open(
                stream=True,
                frames_dir=None,
            ) as session:
                camera.start_camera(session)
                start_time = time.time()

                while (
                    self._capturing.is_set()
                    and (not duration or time.time() < start_time + duration)
                    and (not n_codes or len(codes) < n_codes)
                ):
                    img = camera.capture_frame(session)
                    results = pyzbar.decode(img)

                    if results:
                        results = [
                            result
                            for result in QrcodeDecodedResultSchema().dump(
                                results, many=True
                            )
                            if result['data'] not in last_results
                            or time.time() >= last_results_time + last_results_timeout
                        ]

                    if results:
                        codes.extend(results)
                        get_bus().post(QrcodeScannedEvent(results=results))
                        last_results = {result['data']: result for result in results}
                        last_results_time = time.time()
        finally:
            self._capturing.clear()

        return codes

    @action
    def stop_scanning(self):
        self._capturing.clear()


# vim:sw=4:ts=4:et:
