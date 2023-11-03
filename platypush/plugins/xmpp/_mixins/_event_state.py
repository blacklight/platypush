from abc import ABC

from ._events import XmppEventMixin
from ._state import XmppStateMixin


# pylint: disable=too-few-public-methods
class XmppEventStateMixin(XmppEventMixin, XmppStateMixin, ABC):
    """
    A mixin that encapsulates the state of the XMPP clients and it provides the
    features to handle events.
    """

    def _post_event(self, *args, **kwargs):
        if self._state_serializer:
            self._state_serializer.enqueue(self._state)

        return super()._post_event(*args, **kwargs)
