from typing import List

from platypush.message.event import Event
from platypush.message.response.qrcode import ResultModel


class QrcodeEvent(Event):
    pass


class QrcodeScannedEvent(Event):
    """
    Event triggered when a QR-code or bar code is scanned.
    """
    def __init__(self, results: List[ResultModel], *args, **kwargs):
        super().__init__(*args, results=results, **kwargs)


# vim:sw=4:ts=4:et:
