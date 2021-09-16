from platypush.backend import Backend
from platypush.message.event.scard import SmartCardDetectedEvent, SmartCardRemovedEvent


class ScardBackend(Backend):
    """
    Generic backend to read smart cards and NFC tags and trigger an event
    whenever a device is detected.

    Extend this backend to implement more advanced communication with custom
    smart cards.

    Triggers:

        * :class:`platypush.message.event.scard.SmartCardDetectedEvent` when a smart card is detected
        * :class:`platypush.message.event.scard.SmartCardRemovedEvent` when a smart card is removed

    Requires:

        * **pyscard** (``pip install pyscard``)
    """

    def __init__(self, atr=None, *args, **kwargs):
        """
        :param atr: If set, the backend will trigger events only for card(s) with the specified ATR(s). It can be either an ATR string (space-separated hex octects) or a list of ATR strings.  Default: none (any card will be detected)
        """

        from smartcard.CardType import AnyCardType, ATRCardType
        super().__init__(*args, **kwargs)
        self.ATRs = []

        if atr:
            if isinstance(atr, str):
                self.ATRs = [atr]
            elif isinstance(atr, list):
                self.ATRs = atr
            else:
                raise RuntimeError("Unsupported ATR: \"{}\" - type: {}, " +
                                   "supported types: string, list".format(
                                       atr, type(atr)))

            self.cardtype = ATRCardType(*[self._to_bytes(atr) for atr in self.ATRs])
        else:
            self.cardtype = AnyCardType()

    @staticmethod
    def _to_bytes(data) -> bytes:
        if isinstance(data, str):
            data = data.encode()
        return data

    def run(self):
        from smartcard.CardRequest import CardRequest
        from smartcard.Exceptions import NoCardException, CardConnectionException
        from smartcard.util import toHexString

        super().run()

        self.logger.info('Initialized smart card reader backend - ATR filter: {}'.
                         format(self.ATRs))

        prev_atr = None
        reader = None

        while not self.should_stop():
            try:
                cardrequest = CardRequest(timeout=None, cardType=self.cardtype)
                cardservice = cardrequest.waitforcard()
                cardservice.connection.connect()

                reader = cardservice.connection.getReader()
                atr = toHexString(cardservice.connection.getATR())

                if atr != prev_atr:
                    self.logger.info('Smart card detected on reader {}, ATR: {}'.
                                     format(reader, atr))

                    self.bus.post(SmartCardDetectedEvent(atr=atr, reader=reader))
                    prev_atr = atr
            except Exception as e:
                if isinstance(e, NoCardException) or isinstance(e, CardConnectionException):
                    self.bus.post(SmartCardRemovedEvent(atr=prev_atr, reader=reader))
                else:
                    self.logger.exception(e)

                prev_atr = None

# vim:sw=4:ts=4:et:
