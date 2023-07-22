import asyncio
from typing import Iterable, Optional, Union
from typing_extensions import override

import aioxmpp
import aioxmpp.im
import aioxmpp.muc.xso

from platypush.message.event.xmpp import (
    XmppRoomAffiliationChangedEvent,
    XmppRoomInviteEvent,
    XmppRoomInviteAcceptedEvent,
    XmppRoomInviteRejectedEvent,
    XmppRoomEnterEvent,
    XmppRoomExitEvent,
    XmppRoomJoinEvent,
    XmppRoomLeaveEvent,
    XmppRoomMessageReceivedEvent,
    XmppRoomNickChangedEvent,
    XmppRoomPresenceChangedEvent,
    XmppRoomRoleChangedEvent,
    XmppRoomTopicChangedEvent,
)

from .._types import Errors, XmppPresence
from ._base import XmppBaseHandler


class XmppRoomHandler(XmppBaseHandler):
    """
    Handler for XMPP room events.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.muc_client: aioxmpp.MUCClient = self._client.summon(aioxmpp.MUCClient)
        self.muc_client.on_muc_invitation.connect(self._on_muc_invitation)  # type: ignore

    async def _restore_state(self):
        if self._loaded_state.rooms:
            await asyncio.gather(
                *[
                    self.join(
                        room_id,
                        nick=room.nick if room.nick else self._jid.localpart,
                        password=room.password,
                    )
                    for room_id, room in self._loaded_state.rooms.items()
                ]
            )

    @override
    def restore_state(self):
        self._async_run(self._restore_state, wait_result=False)

    def _on_muc_invitation(
        self,
        _: aioxmpp.stanza.Message,
        room_id: aioxmpp.JID,
        inviter: aioxmpp.JID,
        mode: aioxmpp.im.InviteMode,
        password: Optional[str] = None,
        reason: Optional[str] = None,
        **__,
    ):
        def join():
            assert self._loop, Errors.LOOP
            nick = self._jid.localpart
            self._async_run(
                self.join,
                room_id=jid,
                nick=nick,
                password=password,
                timeout=self.DEFAULT_TIMEOUT,
            )

            self._state.pending_rooms.add(jid)
            self._state.room_invites.pop(jid, None)
            self._post_event(XmppRoomInviteAcceptedEvent, room_id=jid)

        def reject():
            self._state.room_invites.pop(jid, None)
            self._post_event(XmppRoomInviteRejectedEvent, room_id=jid)

        jid = str(room_id)
        invite = self._state.room_invites[jid]
        self._post_user_event(
            XmppRoomInviteEvent,
            room_id=jid,
            user_id=inviter,
            mode=mode.name,
            password=password,
            reason=reason,
        )

        invite.on_accepted = join
        invite.on_rejected = reject
        if self._config.auto_accept_invites:
            invite.accept()

    def _get_occupant_by_jid(
        self, user_id: str, room: aioxmpp.muc.Room
    ) -> aioxmpp.muc.service.Occupant:
        occupant = next(
            iter(
                m
                for m in room.members
                if str(m.conversation_jid) == user_id or str(m.direct_jid) == user_id
            ),
            None,
        )

        assert occupant, Errors.NO_USER
        return occupant

    async def join(
        self,
        room_id: str,
        nick: Optional[str] = None,
        password: Optional[str] = None,
        auto_rejoin: bool = True,
    ):
        address = aioxmpp.JID.fromstr(room_id)
        room, future = self.muc_client.join(
            address,
            nick=nick,
            password=password,
            autorejoin=auto_rejoin,
        )

        await future
        await self._register_room(room)
        return room

    async def leave(self, room_id: str):
        room = self._state.rooms.get(room_id)
        assert room, Errors.ROOM_NOT_JOINED
        await room.leave()
        self._unregister_room(room)

    async def invite(
        self,
        user_id: aioxmpp.JID,
        room_id: str,
        mode: aioxmpp.im.InviteMode = aioxmpp.im.InviteMode.DIRECT,
        text: Optional[str] = None,
    ):
        room = self._state.rooms.get(room_id)
        assert room, Errors.ROOM_NOT_JOINED
        await room.invite(user_id, text=text, mode=mode)

    async def kick(
        self,
        user_id: aioxmpp.JID,
        room_id: str,
        reason: Optional[str] = None,
    ):
        room = self._state.rooms.get(room_id)
        assert room, Errors.ROOM_NOT_JOINED

        occupant = self._get_occupant_by_jid(user_id=str(user_id), room=room)
        await room.kick(occupant, reason=reason)

    async def ban(
        self,
        user_id: aioxmpp.JID,
        room_id: str,
        reason: Optional[str] = None,
    ):
        room = self._state.rooms.get(room_id)
        assert room, Errors.ROOM_NOT_JOINED

        occupant = self._get_occupant_by_jid(user_id=str(user_id), room=room)
        await room.ban(occupant, reason=reason)

    async def set_affiliation(
        self,
        user_id: aioxmpp.JID,
        room_id: str,
        affiliation: str,
        reason: Optional[str] = None,
    ):
        room = self._state.rooms.get(room_id)
        assert room, Errors.ROOM_NOT_JOINED

        occupant = self._get_occupant_by_jid(user_id=str(user_id), room=room)
        await room.muc_set_affiliation(
            occupant.direct_jid or occupant.conversation_jid, affiliation, reason=reason
        )

    async def set_role(
        self,
        user_id: aioxmpp.JID,
        room_id: str,
        role: str,
        reason: Optional[str] = None,
    ):
        room = self._state.rooms.get(room_id)
        assert room, Errors.ROOM_NOT_JOINED

        occupant = self._get_occupant_by_jid(user_id=str(user_id), room=room)
        await room.muc_set_role(occupant.nick, role, reason=reason)

    async def set_topic(self, room_id: str, topic: str):
        room = self._state.rooms.get(room_id)
        assert room, Errors.ROOM_NOT_JOINED
        await room.set_topic(topic)

    async def set_nick(self, room_id: str, nick: str):
        room = self._state.rooms.get(room_id)
        assert room, Errors.ROOM_NOT_JOINED
        await room.set_nick(nick)

    # pylint: disable=too-many-branches
    async def set_room_config(
        self,
        room_id: str,
        name: Optional[bool] = None,
        description: Optional[bool] = None,
        members_only: Optional[bool] = None,
        persistent: Optional[bool] = None,
        moderated: Optional[bool] = None,
        allow_invites: Optional[bool] = None,
        allow_private_messages: Optional[bool] = None,
        allow_change_subject: Optional[bool] = None,
        enable_logging: Optional[bool] = None,
        max_history_fetch: Optional[int] = None,
        max_users: Optional[int] = None,
        password_protected: Optional[bool] = None,
        public: Optional[bool] = None,
        room_admins: Optional[Iterable[Union[str, aioxmpp.JID]]] = None,
        room_owners: Optional[Iterable[Union[str, aioxmpp.JID]]] = None,
        password: Optional[str] = None,
        language: Optional[str] = None,
    ):
        room = self._state.rooms.get(room_id)
        assert room, Errors.ROOM_NOT_JOINED
        config = await self.muc_client.get_room_config(room.jid)
        form = aioxmpp.muc.xso.ConfigurationForm.from_xso(config)

        if members_only is not None:
            form.membersonly.value = members_only
        if persistent is not None:
            form.persistentroom.value = persistent
        if moderated is not None:
            form.moderatedroom.value = moderated
        if description is not None:
            form.roomdesc.value = description
        if name is not None:
            form.roomname.value = name
        if allow_invites is not None:
            form.allowinvites.value = allow_invites
        if allow_private_messages is not None:
            form.allowpm.value = allow_private_messages
        if allow_change_subject is not None:
            form.changesubject.value = allow_change_subject
        if enable_logging is not None:
            form.enablelogging.value = enable_logging
        if max_history_fetch is not None:
            form.maxhistoryfetch.value = max_history_fetch
        if max_users is not None:
            form.maxusers.value = max_users
        if password_protected is not None:
            form.passwordprotectedroom.value = max_users
        if public is not None:
            form.publicroom.value = public
        if password is not None:
            form.roomsecret.value = password
        if language is not None:
            form.lang.value = language
        if room_admins is not None:
            form.roomadmins.value = [
                aioxmpp.JID.fromstr(user_id) if isinstance(user_id, str) else user_id
                for user_id in room_admins
            ]
        if room_owners is not None:
            form.roomowners.value = [
                aioxmpp.JID.fromstr(user_id) if isinstance(user_id, str) else user_id
                for user_id in room_owners
            ]

        await self.muc_client.set_room_config(room.jid, form.render_reply())

    async def _register_room(self, room: aioxmpp.muc.Room):
        room_id = str(room.jid)
        if not self._state.rooms.get(room_id):
            self._register_room_events(room)
            if room_id in self._state.pending_rooms:
                self._state.pending_rooms.remove(room_id)

            self._state.rooms[room_id] = room
            self._post_user_room_event(
                XmppRoomJoinEvent,
                room=room,
                user_id=self._jid,
                is_self=True,
                members=[
                    str(m.direct_jid if m.direct_jid else m.conversation_jid)
                    for m in room.members
                ],
            )

            await self._configure_room_on_join(room)

    async def _configure_room_on_join(self, room: aioxmpp.muc.Room):
        # Check if I'm the owner of the room and there's only me here.
        # If that's the case, odds are that the room has been newly created.
        # Newly created rooms have public_room set to False by default
        if len(room.members) != 1:
            return

        member = room.members[0]
        if not (member.is_self and member.affiliation == "owner"):
            return

        config = await self.muc_client.get_room_config(room.jid)
        form = aioxmpp.muc.xso.ConfigurationForm.from_xso(config)

        # If it's already a persistent room, then it's probably not a room that
        # has just been created
        if form.persistentroom.value:
            return

        form.publicroom.value = True
        form.allowinvites.value = True
        await self.muc_client.set_room_config(room.jid, form.render_reply())

    def _unregister_room(self, room: aioxmpp.muc.Room):
        stored_room = self._state.rooms.pop(self._jid_to_str(room.jid), None)
        if stored_room:
            self._post_user_room_event(
                XmppRoomLeaveEvent,
                room=room,
                user_id=self._jid,
                is_self=True,
            )

    def _register_room_events(self, room: aioxmpp.muc.Room):
        room.on_enter.connect(self._on_room_enter(room))  # type: ignore
        room.on_exit.connect(self._on_room_exit(room))  # type: ignore
        room.on_join.connect(self._on_room_join(room))  # type: ignore
        room.on_leave.connect(self._on_room_leave(room))  # type: ignore
        room.on_message.connect(self._on_msg_received(room))  # type: ignore
        room.on_nick_changed.connect(self._on_room_nick_changed(room))  # type: ignore
        room.on_presence_changed.connect(self._on_room_presence_changed(room))  # type: ignore
        room.on_topic_changed.connect(self._on_room_topic_changed(room))  # type: ignore
        room.on_muc_affiliation_changed.connect(self._on_room_muc_affiliation_changed(room))  # type: ignore
        room.on_muc_role_changed.connect(self._on_room_muc_role_changed(room))  # type: ignore

    def _on_msg_received(self, room: aioxmpp.muc.Room):
        def callback(msg, occupant: aioxmpp.muc.service.Occupant, *_, **__):
            if not msg.body:
                return

            if msg.error:
                self.logger.warning(
                    'Error on message from %s: %s', msg.from_, msg.error
                )

            body = msg.body.lookup([aioxmpp.structs.LanguageRange.fromstr('*')])
            self._post_room_occupant_event(
                XmppRoomMessageReceivedEvent,
                room=room,
                occupant=occupant,
                body=body.rstrip(),
            )

        return callback

    def _on_room_join(self, room: aioxmpp.muc.Room):
        def callback(occupant: aioxmpp.muc.service.Occupant, *_, **__):
            self._post_room_occupant_event(
                XmppRoomJoinEvent, room=room, occupant=occupant
            )

        return callback

    def _on_room_leave(self, room: aioxmpp.muc.Room):
        def callback(occupant: aioxmpp.muc.service.Occupant, *_, **__):
            if occupant.is_self:
                self._unregister_room(room)
            else:
                self._post_room_occupant_event(
                    XmppRoomLeaveEvent, room=room, occupant=occupant
                )

        return callback

    def _on_room_enter(self, room: aioxmpp.muc.Room):
        def callback(*args, **__):
            if args:
                occupant = args[0]
                self._post_room_occupant_event(
                    XmppRoomEnterEvent, room=room, occupant=occupant
                )
            else:
                self._async_run(self._register_room, room)
                self._post_user_room_event(
                    XmppRoomEnterEvent,
                    room=room,
                    user_id=self._jid,
                    is_self=True,
                )

        return callback

    def _on_room_exit(self, room: aioxmpp.muc.Room):
        def callback(
            *args,
            reason: Optional[str] = None,
            **__,
        ):
            if args:
                occupant = args[0]
                self._post_room_occupant_event(
                    XmppRoomExitEvent, room=room, occupant=occupant, reason=reason
                )
            else:
                self._post_user_room_event(
                    XmppRoomExitEvent,
                    room=room,
                    user_id=self._jid,
                    is_self=True,
                    reason=reason,
                )

        return callback

    def _on_room_nick_changed(self, room: aioxmpp.muc.Room):
        def callback(
            member: aioxmpp.muc.service.Occupant,
            old_nick: Optional[str],
            new_nick: Optional[str],
            *_,
            **__,
        ):
            self._post_room_occupant_event(
                XmppRoomNickChangedEvent,
                room=room,
                occupant=member,
                old_nick=old_nick,
                new_nick=new_nick,
            )

        return callback

    def _on_room_presence_changed(self, room: aioxmpp.muc.Room):
        def callback(
            occupant: aioxmpp.muc.service.Occupant,
            _,
            presence: aioxmpp.stanza.Presence,
            **__,
        ):
            self._post_room_occupant_event(
                XmppRoomPresenceChangedEvent,
                room=room,
                occupant=occupant,
                status=aioxmpp.PresenceShow(presence.show).value
                or XmppPresence.AVAILABLE.value,
            )

        return callback

    def _on_room_muc_affiliation_changed(self, room: aioxmpp.muc.Room):
        def callback(
            presence: aioxmpp.stanza.Presence,
            *_,
            actor: Optional[aioxmpp.muc.xso.UserActor] = None,
            reason: Optional[str] = None,
            **__,
        ):
            occupant = self._get_occupant_by_jid(room=room, user_id=str(presence.from_))
            self._post_room_occupant_event(
                XmppRoomAffiliationChangedEvent,
                room=room,
                occupant=occupant,
                affiliation=occupant.affiliation,
                changed_by=str(actor.jid) if actor else None,
                reason=reason,
            )

        return callback

    def _on_room_muc_role_changed(self, room: aioxmpp.muc.Room):
        def callback(
            presence: aioxmpp.stanza.Presence,
            *_,
            actor: Optional[aioxmpp.muc.xso.UserActor] = None,
            reason: Optional[str] = None,
            **__,
        ):
            occupant = self._get_occupant_by_jid(room=room, user_id=str(presence.from_))
            self._post_room_occupant_event(
                XmppRoomRoleChangedEvent,
                room=room,
                occupant=occupant,
                role=occupant.role,
                changed_by=str(actor.jid) if actor else None,
                reason=reason,
            )

        return callback

    def _on_room_topic_changed(self, room: aioxmpp.muc.Room):
        def callback(
            member: aioxmpp.muc.service.ServiceMember,
            topic_map: aioxmpp.structs.LanguageMap,
            **_,
        ):
            topic = topic_map.lookup([aioxmpp.structs.LanguageRange.fromstr('*')])
            self._post_room_event(
                XmppRoomTopicChangedEvent,
                room=room,
                topic=topic,
                changed_by=member.nick,
            )

        return callback

    def send_message(
        self,
        room_id: str,
        body: str,
        language: Optional[str] = None,
    ):
        room = self._state.rooms.get(room_id)
        assert room, Errors.ROOM_NOT_JOINED

        target = room.jid
        msg_type = aioxmpp.MessageType.GROUPCHAT
        lang = language or self._lang
        msg = aioxmpp.Message(type_=msg_type, to=target)
        msg.body.update({lang: body})
        self._client.enqueue(msg)

    def accept_invite(self, room_id: str):
        invite = self._state.room_invites.get(room_id)
        assert invite, Errors.NO_INVITE
        invite.accept()

    def reject_invite(self, room_id: str):
        invite = self._state.room_invites.get(room_id)
        assert invite, Errors.NO_INVITE
        invite.reject()

    async def request_voice(self, room_id: str):
        room = self._state.rooms.get(room_id)
        assert room, Errors.ROOM_NOT_JOINED
        await room.muc_request_voice()
