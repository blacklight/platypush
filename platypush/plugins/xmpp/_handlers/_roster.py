from typing import Union
from typing_extensions import override
import aioxmpp
import aioxmpp.roster.xso

from platypush.message.event.xmpp import (
    XmppContactAddRequestAcceptedEvent,
    XmppContactAddRequestEvent,
    XmppContactAddRequestRejectedEvent,
)

from .._types import Errors
from ._base import XmppBaseHandler


# pylint: disable=too-many-ancestors
class XmppRosterHandler(XmppBaseHandler):
    """
    Handler for XMPP roster events.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.roster: aioxmpp.roster.RosterClient = self._client.summon(
            aioxmpp.roster.RosterClient
        )
        self.roster.on_entry_added.connect(self._on_roster_entry_added)  # type: ignore
        self.roster.on_entry_removed.connect(self._on_roster_entry_removed)  # type: ignore
        self.roster.on_subscribe.connect(self._on_roster_subscribe)  # type: ignore

    @override
    def restore_state(self):
        if self._loaded_state.users:
            for user_id in self._loaded_state.users:
                self.add_user(user_id)

    def _on_roster_entry_added(self, item: aioxmpp.roster.Item, *_, **__):
        self.add_user(item.jid)

    def _on_roster_entry_removed(self, item: aioxmpp.roster.Item, *_, **__):
        self.remove_user(item.jid)

    def _on_roster_subscribe(self, stanza: aioxmpp.stanza.StanzaBase, *_, **__):
        def accept():
            self.add_user(jid)
            self.roster.approve(stanza.from_)
            self._state.user_invites.pop(jid, None)
            self._post_user_event(XmppContactAddRequestAcceptedEvent, user_id=jid)

        def reject():
            self._state.user_invites.pop(jid, None)
            self._post_user_event(XmppContactAddRequestRejectedEvent, user_id=jid)

        if not (isinstance(stanza, aioxmpp.Presence) and stanza.to == self._jid):
            return  # Not a contact add request

        jid = str(stanza.from_)
        invite = self._state.user_invites[jid]
        self._post_user_event(XmppContactAddRequestEvent, user_id=stanza.from_)  # type: ignore
        invite.on_accepted = accept
        invite.on_rejected = reject

        if self._config.auto_accept_invites:
            invite.accept()

    def accept_invite(self, user_id: str):
        invite = self._state.user_invites.get(user_id)
        assert invite, Errors.NO_INVITE
        invite.accept()

    def reject_invite(self, user_id: str):
        invite = self._state.user_invites.get(user_id)
        assert invite, Errors.NO_INVITE
        invite.reject()

    @staticmethod
    def _get_jid(user_id: Union[str, aioxmpp.JID]) -> aioxmpp.JID:
        return (
            user_id
            if isinstance(user_id, aioxmpp.JID)
            else aioxmpp.JID.fromstr(user_id)
        ).replace(resource=None)

    def add_user(self, user_id: Union[str, aioxmpp.JID]):
        """
        Subscribe and add a user to the roster.
        """

        async def async_wrapper(*_, **__):
            self.roster.subscribe(jid)
            await self.roster.set_entry(jid)

        jid = self._get_jid(user_id)
        self._async_run(async_wrapper, wait_result=False)
        self._state.users.add(str(jid))
        self._state.user_invites.pop(str(jid), None)

        if self._state_serializer:
            self._state_serializer.enqueue(self._state)

    def remove_user(self, user_id: Union[str, aioxmpp.JID]):
        """
        Remove a user from the roster.
        """

        async def async_wrapper(*_, **__):
            self.roster.unsubscribe(jid)
            await self.roster.remove_entry(jid)

        jid = self._get_jid(user_id)
        self._async_run(async_wrapper, wait_result=False)
        self._state.user_invites.pop(str(jid), None)

        if str(jid) in self._state.users:
            self._state.users.remove(str(jid))
        if self._state_serializer:
            self._state_serializer.enqueue(self._state)
