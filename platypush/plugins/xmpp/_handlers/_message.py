import aioxmpp
import aioxmpp.dispatcher

from platypush.message.event.xmpp import (
    XmppMessageReceivedEvent,
)

from ._base import XmppBaseHandler


# pylint: disable=too-many-ancestors,too-few-public-methods
class XmppMessageHandler(XmppBaseHandler):
    """
    Handler for XMPP message events.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dispatcher = self._client.summon(
            aioxmpp.dispatcher.SimpleMessageDispatcher
        )
        self.dispatcher.register_callback(
            aioxmpp.MessageType.CHAT,
            None,  # from filter
            self._on_msg_received,
        )

    def _on_msg_received(self, msg, *_, **__):
        if not msg.body:
            return

        if msg.error:
            self.logger.warning('Error on message from %s: %s', msg.from_, msg.error)

        body = msg.body.lookup([aioxmpp.structs.LanguageRange.fromstr('*')])
        self._post_user_event(
            XmppMessageReceivedEvent, user_id=msg.from_, body=body.rstrip()
        )
