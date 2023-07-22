from typing import Union

import aioxmpp

from platypush.message.event.xmpp import (
    XmppPresenceChangedEvent,
    XmppRoomUserAvailableEvent,
    XmppRoomUserUnavailableEvent,
    XmppUserAvailableEvent,
    XmppUserUnavailableEvent,
)

from .._types import XmppPresence
from ._base import XmppBaseHandler


# pylint: disable=too-many-ancestors
class XmppPresenceHandler(XmppBaseHandler):
    """
    Handler for XMPP presence events.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.presence_client: aioxmpp.PresenceClient = self._client.summon(
            aioxmpp.PresenceClient
        )
        self.presence_client.on_changed.connect(self._on_presence_changed)  # type: ignore
        self.presence_client.on_available.connect(self._on_presence_available)  # type: ignore
        self.presence_client.on_unavailable.connect(self._on_presence_unavailable)  # type: ignore

        self.presence_server: aioxmpp.PresenceServer = self._client.summon(
            aioxmpp.PresenceServer
        )

    def _is_room_event(self, jid: aioxmpp.JID) -> bool:
        jid_str = str(jid.replace(resource=None))  # type: ignore
        return (
            self._state.rooms.get(jid_str) is not None
            or jid_str in self._state.pending_rooms
        )

    def _on_presence_changed(
        self,
        user_id: Union[str, aioxmpp.JID],
        presence: aioxmpp.stanza.Presence,
        **_,
    ):
        if isinstance(user_id, aioxmpp.JID) and self._is_room_event(user_id):
            return  # Rooms will have their own presence changed events

        self._post_user_event(
            XmppPresenceChangedEvent,
            user_id=user_id,
            status=aioxmpp.PresenceShow(presence.show).value
            or XmppPresence.AVAILABLE.value,
        )

    def _on_presence_available(self, user_id: aioxmpp.JID, *_, **__):
        jid = str(user_id)
        if self._is_room_event(user_id):
            self._post_user_event(
                XmppRoomUserAvailableEvent,
                user_id=jid,
                room_id=str(user_id.replace(resource=None)),
                is_self=jid == str(self._jid),
            )
        elif jid in self._state.users:
            self._state.users.add(jid)
            self._post_user_event(XmppUserAvailableEvent, user_id=user_id)

    def _on_presence_unavailable(self, user_id: aioxmpp.JID, *_, **__):
        jid = str(user_id)
        if self._is_room_event(user_id):
            self._post_user_event(
                XmppRoomUserUnavailableEvent,
                user_id=jid,
                room_id=str(user_id.replace(resource=None)),
                is_self=jid == str(self._jid),
            )
        elif jid in self._state.users:
            self._post_user_event(XmppUserUnavailableEvent, user_id=user_id)

    def set_presence(self, presence: XmppPresence):
        available = presence.value != XmppPresence.OFFLINE.value
        presence_show = aioxmpp.PresenceShow(
            None
            if presence.value
            in {XmppPresence.AVAILABLE.value, XmppPresence.OFFLINE.value}
            else presence.value
        )

        self.presence_server.set_presence(
            aioxmpp.PresenceState(
                available=available,
                show=presence_show,
            )
        )
