from abc import ABC, abstractmethod
from typing import Optional

from .._state import SerializedState, StateSerializer, XmppState
from ._base import XmppBaseMixin


# pylint: disable=too-few-public-methods
class XmppStateMixin(XmppBaseMixin, ABC):
    """
    A simple mixin that encapsulates an XMPP state object.
    """

    @abstractmethod
    def __init__(
        self,
        *args,
        state: Optional[XmppState] = None,
        loaded_state: Optional[SerializedState] = None,
        state_serializer: Optional[StateSerializer] = None,
        **kwargs,
    ):
        self._state = state or XmppState()
        self._loaded_state = loaded_state or SerializedState()
        self._state_serializer = state_serializer
        super().__init__(*args, **kwargs)

    def restore_state(self):
        """
        Function called by the plugin once connected to notify that the
        component should reload the previous state (optional, to be implemented
        by derived classes).
        """
