import logging
import json

from smartcard.CardType import AnyCardType, ATRCardType
from smartcard.CardRequest import CardRequest
from smartcard.Exceptions import NoCardException
from smartcard.util import toHexString

from platypush.backend import Backend
from platypush.message.event.scard import SmartCardDetectedEvent, SmartCardRemovedEvent


class ScardBackend(Backend):
    """
    Generic backend to read smart cards and trigger SmartCardDetectedEvent
    messages with the card ATR whenever a card is detected. It requires
    pyscard https://pypi.org/project/pyscard/

    Extend this backend to implement more advanced communication with
    custom smart cards.
    """

    def __init__(self, atr=None, *args, **kwargs):
        """
        Params:
            atr -- If set, the backend will trigger events only for card(s)
                with the specified ATR(s). It can be either an ATR string
                (space-separated hex octects) or a list of ATR strings.
                Default: none (any card will be detected)
        """
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

            self.cardtype = ATRCardType( *[toBytes(atr) for atr in self.ATRs] )
        else:
            self.cardtype = AnyCardType()


    def run(self):
        super().run()

        logging.info('Initialized smart card reader backend - ATR filter: {}'.
                     format(self.ATRs))

        prev_atr = None
        while not self.should_stop():
            try:
                cardrequest = CardRequest(timeout=None, cardType=self.cardtype)
                cardservice = cardrequest.waitforcard()
                cardservice.connection.connect()

                reader = cardservice.connection.getReader()
                atr = toHexString(cardservice.connection.getATR())

                if atr != prev_atr:
                    logging.info('Smart card detected on reader {}, ATR: {}'.
                                format(reader, atr))

                    self.bus.post(SmartCardDetectedEvent(atr=atr, reader=reader))
                    prev_atr = atr
            except Exception as e:
                prev_atr = None

                if isinstance(e, NoCardException):
                    self.bus.post(SmartCardRemovedEvent())
                else:
                    logging.exception(e)


# vim:sw=4:ts=4:et:

