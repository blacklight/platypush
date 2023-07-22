from typing import Optional, Union

from platypush.message.event.xmpp import XmppDisconnectedEvent

from ._base import XmppBaseHandler


# pylint: disable=too-many-ancestors
class XmppConnectionHandler(XmppBaseHandler):
    """
    Handler for XMPP connection/disconnection events.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client.on_failure.connect(self._on_disconnect())  # type: ignore
        self._client.on_stopped.connect(self._on_disconnect())  # type: ignore

    def _on_disconnect(self, reason: Optional[Union[str, Exception]] = None):
        def callback(*_, **__):
            if not self._state.disconnect_notified.is_set():
                self._post_event(XmppDisconnectedEvent, reason=reason)
            self._state.disconnect_notified.set()

        return callback

    def disconnect(self, reason: Optional[Union[str, Exception]] = None):
        self._on_disconnect(reason=reason)()
