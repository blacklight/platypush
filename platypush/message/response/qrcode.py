import base64
from typing import Optional, List

from pyzbar.pyzbar import Decoded
from pyzbar.locations import Rect

from platypush.message import Mapping
from platypush.message.response import Response


class QrcodeResponse(Response):
    pass


class QrcodeGeneratedResponse(QrcodeResponse):
    # noinspection PyShadowingBuiltins
    def __init__(self,
                 content: str,
                 format: str,
                 data: Optional[str] = None,
                 image_file: Optional[str] = None,
                 *args, **kwargs):
        super().__init__(*args, output={
            'text': content,
            'data': data,
            'format': format,
            'image_file': image_file,
        }, **kwargs)


class RectModel(Mapping):
    def __init__(self, rect: Rect):
        super().__init__()
        self.left = rect.left
        self.top = rect.top
        self.width = rect.width
        self.height = rect.height


class ResultModel(Mapping):
    def __init__(self, result: Decoded, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            data = result.data.decode()
        except (ValueError, TypeError):
            data = base64.encodebytes(result.data).decode()

        self.data = data
        self.type = result.type
        self.rect = dict(RectModel(result.rect)) if result.rect else {}


class QrcodeDecodedResponse(QrcodeResponse):
    def __init__(self, results: List[Decoded], image_file: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, output={
            'image_file': image_file,
            'results': [dict(ResultModel(result)) for result in results],
        }, **kwargs)


# vim:sw=4:ts=4:et:
