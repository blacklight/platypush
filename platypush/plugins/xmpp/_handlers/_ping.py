import aioxmpp

from ._base import XmppBaseHandler


# pylint: disable=too-many-ancestors,too-few-public-methods
class XmppPingHandler(XmppBaseHandler):
    """
    Handler for the XMPP ping logic.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ping: aioxmpp.PingService = self._client.summon(aioxmpp.PingService)
