from typing import List

from platypush.message.event import Event


class QrcodeScannedEvent(Event):
    """
    Event triggered when a QR-code or bar code is scanned.
    """

    def __init__(self, results: List[dict], *args, **kwargs):
        """
        :param results: List of decoded QR code results:

            .. schema:: qrcode.QrcodeDecodedResultSchema(many=True)
        """
        super().__init__(*args, results=results, **kwargs)


# vim:sw=4:ts=4:et:
