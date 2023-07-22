from typing import Optional

import aioxmpp
import aioxmpp.im.p2p

from platypush.message.event.xmpp import (
    XmppConversationAddedEvent,
    XmppConversationEnterEvent,
    XmppConversationExitEvent,
    XmppConversationJoinEvent,
    XmppConversationLeaveEvent,
)

from ._base import XmppBaseHandler


# pylint: disable=too-many-ancestors
class XmppConversationHandler(XmppBaseHandler):
    """
    Handler for XMPP conversation events.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversation: aioxmpp.im.ConversationService = self._client.summon(
            aioxmpp.im.ConversationService
        )
        self.conversation.on_conversation_added.connect(self._on_conversation_added)  # type: ignore

    def _on_conversation_added(
        self, conversation: aioxmpp.im.p2p.Conversation, *_, **__
    ):
        if not isinstance(conversation, aioxmpp.im.p2p.Conversation):
            return  # Don't add signals to rooms - they'll have their own

        conversation_id = str(conversation.jid)
        if not self._state.conversations.get(conversation_id):
            self._register_conversation_events(conversation)
            self._state.users.add(conversation_id)
            self._state.conversations[conversation_id] = conversation
            self._post_conversation_event(
                XmppConversationAddedEvent,
                conversation=conversation,
                members=[
                    str(m.direct_jid if m.direct_jid else m.conversation_jid)
                    for m in conversation.members
                ],
            )

    def _register_conversation_events(self, conversation: aioxmpp.im.p2p.Conversation):
        if not isinstance(conversation, aioxmpp.im.p2p.Conversation):
            return  # Don't add signals to rooms - they'll have their own

        conversation.on_enter.connect(self._on_conversation_enter(conversation))  # type: ignore
        conversation.on_exit.connect(self._on_conversation_exit(conversation))  # type: ignore
        conversation.on_join.connect(self._on_conversation_join(conversation))  # type: ignore
        conversation.on_leave.connect(self._on_conversation_leave(conversation))  # type: ignore

    def _on_conversation_enter(self, conversation: aioxmpp.im.p2p.Conversation):
        def callback(*_, **__):
            self._post_conversation_event(XmppConversationEnterEvent, conversation)

        return callback

    def _on_conversation_exit(self, conversation: aioxmpp.im.p2p.Conversation):
        def callback(*_, **__):
            self._post_conversation_event(XmppConversationExitEvent, conversation)

        return callback

    def _on_conversation_join(self, conversation: aioxmpp.im.p2p.Conversation):
        def callback(member: aioxmpp.im.p2p.Member, *_, **__):
            self._post_conversation_member_event(
                XmppConversationJoinEvent, conversation=conversation, member=member
            )

        return callback

    def _on_conversation_leave(self, conversation: aioxmpp.im.p2p.Conversation):
        def callback(member: aioxmpp.im.p2p.Member, *_, **__):
            if member.is_self:
                user_id = str(conversation.jid)
                # Remove the conversation from the map of active conversations
                self._state.conversations.pop(user_id, None)
                self._state.users = self._state.users.difference({user_id})

            self._post_conversation_member_event(
                XmppConversationLeaveEvent,
                conversation=conversation,
                member=member,
            )

        return callback

    def send_message(
        self,
        user_id: str,
        body: str,
        language: Optional[str] = None,
    ):
        lang = language or self._lang
        msg = aioxmpp.Message(
            type_=aioxmpp.MessageType.CHAT, to=aioxmpp.JID.fromstr(user_id)
        )
        msg.body.update({lang: body})
        self._client.enqueue(msg)
