from abc import ABC
from typing import Optional, Type, Union

import aioxmpp
import aioxmpp.im.p2p

from platypush.context import get_bus
from platypush.message.event.xmpp import XmppEvent

from ._base import XmppBaseMixin


# pylint: disable=too-few-public-methods
class XmppEventMixin(XmppBaseMixin, ABC):
    """
    This mixin provides utility methods to post XMPP events.
    """

    def _post_event(self, event_type: Type[XmppEvent], *args, **kwargs):
        get_bus().post(
            event_type(
                *args,
                client_jabber_id=self._jid_to_str(
                    self._client.local_jid if self._client else self._jid
                ),
                **kwargs,
            )
        )

    def _post_user_event(
        self,
        event_type: Type[XmppEvent],
        user_id: Union[str, aioxmpp.JID],
        *args,
        **kwargs,
    ):
        if isinstance(user_id, str):
            kwargs['user_id'] = user_id
            kwargs['jid'] = user_id
        else:
            kwargs['user_id'] = self._jid_to_str(user_id)
            kwargs['jid'] = str(user_id)

        self._post_event(event_type, *args, **kwargs)

    def _post_room_event(
        self, event_type: Type[XmppEvent], room: aioxmpp.muc.Room, *args, **kwargs
    ):
        self._post_event(
            event_type, *args, room_id=self._jid_to_str(room.jid), **kwargs
        )

    def _post_user_room_event(
        self,
        event_type: Type[XmppEvent],
        room: aioxmpp.muc.Room,
        user_id: Union[str, aioxmpp.JID],
        *args,
        **kwargs,
    ):
        self._post_user_event(
            event_type,
            *args,
            user_id=user_id,
            room_id=self._jid_to_str(room.jid),
            **kwargs,
        )

    def _post_conversation_event(
        self,
        event_type: Type[XmppEvent],
        conversation: aioxmpp.im.p2p.Conversation,
        *args,
        **kwargs,
    ):
        self._post_event(
            event_type, *args, conversation_id=str(conversation.jid), **kwargs
        )

    def _post_room_occupant_event(
        self,
        event_type: Type[XmppEvent],
        room: aioxmpp.muc.Room,
        occupant: aioxmpp.muc.service.Occupant,
        *args,
        user_id: Optional[str] = None,
        **kwargs,
    ):
        self._post_user_room_event(
            event_type,
            *args,
            room=room,
            user_id=user_id
            or (
                occupant.direct_jid
                if occupant.direct_jid
                else occupant.conversation_jid
            ),
            is_self=occupant.is_self,
            **kwargs,
        )

    def _post_conversation_member_event(
        self,
        event_type: Type[XmppEvent],
        conversation: aioxmpp.im.p2p.Conversation,
        member: aioxmpp.im.p2p.Member,
        *args,
        user_id: Optional[str] = None,
        **kwargs,
    ):
        self._post_conversation_event(
            event_type,
            *args,
            conversation=conversation,
            user_id=user_id
            or (
                self._jid_to_str(member.direct_jid)
                if member.direct_jid
                else str(member.conversation_jid)
            ),
            is_self=member.is_self,
            **kwargs,
        )
