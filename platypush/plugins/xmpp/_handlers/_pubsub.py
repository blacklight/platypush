import aioxmpp

from ._base import XmppBaseHandler


# pylint: disable=too-many-ancestors,too-few-public-methods
class XmppPubSubHandler(XmppBaseHandler):
    """
    Handler for XMPP pub/sub events.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pubsub: aioxmpp.PubSubClient = self._client.summon(aioxmpp.PubSubClient)
