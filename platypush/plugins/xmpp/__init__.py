import os
from typing import Iterable, Optional, Type, Union
from typing_extensions import override

import aioxmpp
import aioxmpp.im

from platypush.config import Config
from platypush.message.event.xmpp import XmppConnectedEvent
from platypush.plugins import AsyncRunnablePlugin, action

from ._base import XmppBasePlugin
from ._config import XmppConfig
from ._handlers import (
    XmppBaseHandler,
    XmppConnectionHandler,
    XmppConversationHandler,
    XmppHandlersRegistry,
    XmppPresenceHandler,
    XmppRoomHandler,
    XmppRosterHandler,
    discover_handlers,
)
from ._mixins import XmppBaseMixin
from ._state import SerializedState, StateSerializer
from ._types import Errors, XmppPresence


# pylint: disable=too-many-ancestors
class XmppPlugin(AsyncRunnablePlugin, XmppBasePlugin):
    """
    XMPP integration.

    Requires:

        * **aioxmpp** (``pip install aioxmpp``)
        * **pytz** (``pip install pytz``)

    Triggers:

        * :class:`platypush.message.event.xmpp.XmppConnectedEvent`
        * :class:`platypush.message.event.xmpp.XmppContactAddRequestAcceptedEvent`
        * :class:`platypush.message.event.xmpp.XmppContactAddRequestEvent`
        * :class:`platypush.message.event.xmpp.XmppContactAddRequestRejectedEvent`
        * :class:`platypush.message.event.xmpp.XmppConversationAddedEvent`
        * :class:`platypush.message.event.xmpp.XmppConversationEnterEvent`
        * :class:`platypush.message.event.xmpp.XmppConversationExitEvent`
        * :class:`platypush.message.event.xmpp.XmppConversationJoinEvent`
        * :class:`platypush.message.event.xmpp.XmppConversationLeaveEvent`
        * :class:`platypush.message.event.xmpp.XmppConversationNickChangedEvent`
        * :class:`platypush.message.event.xmpp.XmppDisconnectedEvent`
        * :class:`platypush.message.event.xmpp.XmppMessageReceivedEvent`
        * :class:`platypush.message.event.xmpp.XmppPresenceChangedEvent`
        * :class:`platypush.message.event.xmpp.XmppRoomAffiliationChangedEvent`
        * :class:`platypush.message.event.xmpp.XmppRoomEnterEvent`
        * :class:`platypush.message.event.xmpp.XmppRoomExitEvent`
        * :class:`platypush.message.event.xmpp.XmppRoomInviteAcceptedEvent`
        * :class:`platypush.message.event.xmpp.XmppRoomInviteEvent`
        * :class:`platypush.message.event.xmpp.XmppRoomInviteRejectedEvent`
        * :class:`platypush.message.event.xmpp.XmppRoomJoinEvent`
        * :class:`platypush.message.event.xmpp.XmppRoomLeaveEvent`
        * :class:`platypush.message.event.xmpp.XmppRoomMessageReceivedEvent`
        * :class:`platypush.message.event.xmpp.XmppRoomNickChangedEvent`
        * :class:`platypush.message.event.xmpp.XmppRoomPresenceChangedEvent`
        * :class:`platypush.message.event.xmpp.XmppRoomRoleChangedEvent`
        * :class:`platypush.message.event.xmpp.XmppRoomTopicChangedEvent`
        * :class:`platypush.message.event.xmpp.XmppRoomUserAvailableEvent`
        * :class:`platypush.message.event.xmpp.XmppRoomUserUnavailableEvent`
        * :class:`platypush.message.event.xmpp.XmppUserAvailableEvent`
        * :class:`platypush.message.event.xmpp.XmppUserUnavailableEvent`

    """

    def __init__(
        self,
        user_id: str,
        password: Optional[str] = None,
        language: Optional[str] = None,
        anonymous: bool = False,
        auto_accept_invites: bool = True,
        restore_state: bool = True,
        state_file: Optional[str] = None,
        **kwargs,
    ):
        """
        :param user_id: Jabber/user ID, in the format ``user@example.org``.
        :param password: User password.
        :param language: ISO string for the language code that will be used by
            the bot (default: ``None``).
        :param anonymous: Whether to use anonymous authentication (default:
            ``False``).
        :param auto_accept_invites: Whether to automatically accept invites to
            conversations (default: True). If set to False, and you still want
            some control on which invites should be accepted, you can create a
            ``hook`` on
            :class:`platypush.message.event.xmpp.XmppRoomInviteEvent` that
            calls either :meth:`.accept_invite` or :meth:`.reject_invite` with
            the ``room_id`` specified on the event, if it is a room event, or
            subscribe to
            :class:`platypush.message.event.xmpp.XmppContactAddRequestEvent`
            and call either :meth:`.accept_invite` or :meth:`.reject_invite`
            with the ``user_id`` specified on the event, if it is a contact add
            request.
        :param restore_state: If ``True`` (default) then any previously joined
            conversation or subscribed contact will be joined/subscribed again
            when the plugin restarts. Otherwise, upon restart the plugin will
            start from a state with no subscriptions nor joined rooms.
        :param state_file: Path where the previous state will be stored, if
            ``restore_state`` is ``True``. Default:
            ``<WORKDIR>/xmpp/state.json``.
        """
        super(XmppBasePlugin, self).__init__(user_id=user_id, language=language)
        super(AsyncRunnablePlugin, self).__init__(**kwargs)

        self._security = aioxmpp.make_security_layer(password, anonymous=anonymous)
        self._config = XmppConfig(
            auto_accept_invites=auto_accept_invites,
            restore_state=restore_state,
            state_file=os.path.expanduser(
                state_file or os.path.join(Config.workdir, 'xmpp', 'state.json')
            ),
        )
        self._loaded_state = SerializedState()
        self._state_serializer = StateSerializer(user_id=self._jid, config=self._config)
        self._handlers = XmppHandlersRegistry(self)
        self.restore_state()

    def restore_state(self):
        """
        Reload the previous state from the configured state file.
        """
        if not (self._config.state_file and self._config.restore_state):
            return

        self._loaded_state = self._state_serializer.load()

    @property
    def _conn_handler(self) -> XmppConnectionHandler:
        return self._handlers[XmppConnectionHandler]

    @property
    def _conv_handler(self) -> XmppConversationHandler:
        return self._handlers[XmppConversationHandler]

    @property
    def _presence_handler(self) -> XmppPresenceHandler:
        return self._handlers[XmppPresenceHandler]

    @property
    def _room_handler(self) -> XmppRoomHandler:
        return self._handlers[XmppRoomHandler]

    @property
    def _roster_handler(self) -> XmppRosterHandler:
        return self._handlers[XmppRosterHandler]

    def _on_disconnect(self, reason: Optional[Union[str, Exception]] = None):
        self._conn_handler.disconnect(reason)

    def _register_handlers(self):
        for hndl_type in discover_handlers():
            hndl = self.register_xmpp_handler(hndl_type)
            hndl.restore_state()

    def register_xmpp_handler(self, hndl_type: Type[XmppBaseMixin]) -> XmppBaseHandler:
        self.logger.debug('Registering handler: %s', hndl_type)
        self._handlers[hndl_type] = hndl_type(
            user_id=self._jid,
            language=self._lang,
            config=self._config,
            state=self._state,
            client=self._client,
            loop=self._loop,
            state_serializer=self._state_serializer,
            loaded_state=self._loaded_state,
        )

        return self._handlers[hndl_type]

    @override
    def should_stop(self) -> bool:
        return super().should_stop() or self._state.should_stop.is_set()

    @override
    def stop(self):
        self._state.should_stop.set()
        self._stop_state_serializer()
        self._stop_client()
        self._on_disconnect(reason='Plugin terminated')
        super().stop()

    def _stop_state_serializer(self):
        if self._state_serializer:
            self._state_serializer.flush()
            self._state_serializer.wait(self._state_serializer.flush_timeout)

    def _stop_client(self):
        if self._client:
            self._client.stop()
            self._client = None

    @override
    async def listen(self):
        self._client = aioxmpp.PresenceManagedClient(self._jid, self._security)

        try:
            async with self._client.connected():
                self._register_handlers()
                self._post_event(XmppConnectedEvent)
                await self._state.should_stop.wait()
        except Exception as e:
            self.logger.warning('XMPP connection error: %s', e)
            self.logger.exception(e)
            self._on_disconnect(e)
            raise e

    @action
    def send_message(
        self,
        body: str,
        user_id: Optional[str] = None,
        room_id: Optional[str] = None,
        language: Optional[str] = None,
    ):
        """
        Send a message to a target (the Jabber ID of another user or room).

        :param body: Message body.
        :param user_id: Jabber ID of the target user. Either user_id or room_id
            should be specified.
        :param room_id: Jabber ID of the target room. Either user_id or room_id
            should be specified.
        :param language: Override the default language code.
        """
        if room_id:
            self._room_handler.send_message(
                room_id=room_id, body=body, language=language
            )
        elif user_id:
            self._conv_handler.send_message(
                user_id=user_id, body=body, language=language
            )
        else:
            raise AssertionError(Errors.USER_ID_OR_ROOM_ID)

    @action
    def join(
        self,
        room_id: str,
        nick: Optional[str] = None,
        password: Optional[str] = None,
        auto_rejoin: bool = True,
        timeout: Optional[float] = XmppBaseMixin.DEFAULT_TIMEOUT,
    ):
        """
        Join a room/conversation.

        :param room_id: The Jabber ID of the conversation to join.
        :param nick: The nickname that the bot should use in the room (default:
            the nickname specified in the configuration's ``user_id``
            parameter).
        :param password: The password of the room (default: None).
        :param auto_rejoin: Whether to automatically rejoin the room after
            disconnection/kick (default: True).
        :param timeout: Room join timeout (default: 20 seconds). Set to null
            for no timeout.
        """
        nick = nick or self._jid.localpart
        self._async_run(
            self._room_handler.join,
            room_id,
            timeout=timeout,
            nick=nick,
            password=password,
            auto_rejoin=auto_rejoin,
        )

    @action
    def leave(
        self, room_id: str, timeout: Optional[float] = XmppBaseMixin.DEFAULT_TIMEOUT
    ):
        """
        Leave a room/conversation.

        :param room_id: The Jabber ID of the conversation to leave.
        :param timeout: Room leave timeout (default: 20 seconds). Set to null
            for no timeout.
        """
        self._async_run(
            self._room_handler.leave,
            room_id,
            timeout=timeout,
        )

    @action
    def accept_invite(
        self, room_id: Optional[str] = None, user_id: Optional[str] = None
    ):
        """
        Accept a pending invite to a multi-user conversation or a contact add
        request.

        :param user_id: The target ``user_id`` if this is a contact add request.
        :param room_id: The target ``room_id`` if this is a room invite request.
        """
        if room_id:
            self._room_handler.accept_invite(room_id)
        elif user_id:
            self._roster_handler.accept_invite(user_id)
        else:
            raise AssertionError(Errors.USER_ID_OR_ROOM_ID)

    @action
    def reject_invite(
        self, room_id: Optional[str] = None, user_id: Optional[str] = None
    ):
        """
        Reject a pending invite to a multi-user conversation or a contact add
        request.

        :param user_id: The target ``user_id`` if this is a contact add request.
        :param room_id: The target ``room_id`` if this is a room invite request.
        """
        if room_id:
            self._room_handler.reject_invite(room_id)
        elif user_id:
            self._roster_handler.reject_invite(user_id)
        else:
            raise AssertionError(Errors.USER_ID_OR_ROOM_ID)

    @action
    def invite(
        self,
        room_id: str,
        user_id: str,
        mode: str = 'direct',
        text: Optional[str] = None,
        timeout: Optional[float] = XmppBaseMixin.DEFAULT_TIMEOUT,
    ):
        """
        Invite a user to a room.

        :param room_id: The target room JID.
        :param user_id: The JID of the user to invite.
        :param timeout: Invite request send timeout (default: 20 seconds). Set
            to null for no timeout.
        :param mode: Invite mode - can be ``direct`` (default) or ``mediated``.

           - ``direct``: The invitation is sent directly to the invitee,
             without going through a service specific to the conversation.

           - ``mediated``: The invitation is sent indirectly through a service
             which is providing the conversation. Advantages of using this mode
             include most notably that the service can automatically add the
             invitee to the list of allowed participants in configurations
             where such restrictions exist (or deny the request if the inviter
             does not have the permissions to do so).
        :param text: Optional text to send with the invitation.
        """
        self._async_run(
            self._room_handler.invite,
            room_id=room_id,
            user_id=aioxmpp.JID.fromstr(user_id),
            mode=getattr(
                aioxmpp.im.InviteMode, mode.upper(), aioxmpp.im.InviteMode.DIRECT
            ),
            text=text,
            timeout=timeout,
        )

    @action
    def set_presence(self, presence: Union[str, XmppPresence]):
        """
        Set/broadcast a new presence state for the user.

        :param presence: The new presence state. Possible values are:

            - ``available``
            - ``offline``
            - ``away``
            - ``xa``
            - ``chat``
            - ``dnd``

        """
        pres = XmppPresence(presence.lower()) if isinstance(presence, str) else presence
        self._presence_handler.set_presence(pres)

    @action
    def set_affiliation(
        self,
        room_id: str,
        user_id: str,
        affiliation: str,
        reason: Optional[str] = None,
        timeout: Optional[float] = XmppBaseMixin.DEFAULT_TIMEOUT,
    ):
        """
        Change the affiliation of a user to a room.

        :param room_id: The target room JID.
        :param user_id: The user JID.
        :param affiliation: The affiliation to set. Possible values are:

            - ``owner``
            - ``member``
            - ``none``
            - ``outcast``
            - ``publisher``
            - ``publish-only``

        :param timeout: Request timeout (default: 20 seconds). Set to null for
            no timeout.
        :param reason: Optional reason for the change.
        """
        self._async_run(
            self._room_handler.set_affiliation,
            room_id=room_id,
            user_id=aioxmpp.JID.fromstr(user_id),
            affiliation=affiliation,
            reason=reason,
            timeout=timeout,
        )

    @action
    def set_role(
        self,
        room_id: str,
        user_id: str,
        role: str,
        reason: Optional[str] = None,
        timeout: Optional[float] = XmppBaseMixin.DEFAULT_TIMEOUT,
    ):
        """
        Change the role of a user in a room.

        :param room_id: The target room JID.
        :param user_id: The user JID.
        :param role: The role to set. Possible values are:

            - ``none``
            - ``participant``
            - ``visitor``
            - ``moderator``

        :param timeout: Request timeout (default: 20 seconds). Set to null for
            no timeout.
        :param reason: Optional reason for the change.
        """
        self._async_run(
            self._room_handler.set_role,
            room_id=room_id,
            user_id=aioxmpp.JID.fromstr(user_id),
            role=role,
            reason=reason,
            timeout=timeout,
        )

    @action
    def kick(
        self,
        room_id: str,
        user_id: str,
        reason: Optional[str] = None,
        timeout: Optional[float] = XmppBaseMixin.DEFAULT_TIMEOUT,
    ):
        """
        Kick a user from a room.

        :param room_id: The target room JID.
        :param user_id: The JID of the user to kick.
        :param timeout: Request timeout (default: 20 seconds). Set to null for
            no timeout.
        :param reason: Kick reason.
        """
        self._async_run(
            self._room_handler.kick,
            room_id=room_id,
            user_id=aioxmpp.JID.fromstr(user_id),
            reason=reason,
            timeout=timeout,
        )

    @action
    def ban(
        self,
        room_id: str,
        user_id: str,
        reason: Optional[str] = None,
        timeout: Optional[float] = XmppBaseMixin.DEFAULT_TIMEOUT,
    ):
        """
        Ban a user from a room.

        :param room_id: The target room JID.
        :param user_id: The JID of the user to ban.
        :param timeout: Request timeout (default: 20 seconds). Set to null for
            no timeout.
        :param reason: Ban reason.
        """
        self._async_run(
            self._room_handler.ban,
            room_id=room_id,
            user_id=aioxmpp.JID.fromstr(user_id),
            reason=reason,
            timeout=timeout,
        )

    @action
    def set_topic(
        self,
        room_id: str,
        topic: str,
        timeout: Optional[float] = XmppBaseMixin.DEFAULT_TIMEOUT,
    ):
        """
        Set the topic of a room.

        :param room_id: The target room JID.
        :param topic: New topic.
        :param timeout: Request timeout (default: 20 seconds). Set to null for
            no timeout.
        """
        self._async_run(
            self._room_handler.set_topic,
            room_id=room_id,
            topic=topic,
            timeout=timeout,
        )

    @action
    def set_room_configuration(
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
        room_admins: Optional[Iterable[str]] = None,
        room_owners: Optional[Iterable[str]] = None,
        password: Optional[str] = None,
        language: Optional[str] = None,
        timeout: Optional[float] = XmppBaseMixin.DEFAULT_TIMEOUT,
    ):
        """
        Changes the configuration of a room.

        All the parameters are optional, and only those that have a non-null
        value will be set.

        :param room_id: The target room JID.
        :param name: New room name.
        :param description: New room description.
        :param members_only: Whether or not this room is only for members.
        :param persistent: Whether or not this room is persistent.
        :param moderated: Whether or not this room is moderated.
        :param allow_invites: Whether or not this room allows invites.
        :param allow_private_messages: Whether or not this room allows private
            messages.
        :param allow_change_subject: Whether or not this room allows changing
            its subject.
        :param enable_logging: Whether or not this room has logging enabled.
        :param max_history_fetch: Maximum number of past messages to fetch when
            joining the room.
        :param max_users: Maximum number of users allowed in the room.
        :param password_protected: Whether or not this room is password protected.
        :param public: Whether or not this room is publicly visible.
        :param room_admins: List of room admins, by Jabber ID.
        :param room_owners: List of room owners, by Jabber ID.
        :param password: If the room is password protected, configure its
            password here.
        :param language: Language of the room (ISO 2-letter code).
        :param timeout: Request timeout (default: 20 seconds). Set to null for
            no timeout.
        """
        self._async_run(
            self._room_handler.set_room_config,
            room_id=room_id,
            name=name,
            description=description,
            members_only=members_only,
            persistent=persistent,
            moderated=moderated,
            allow_invites=allow_invites,
            allow_private_messages=allow_private_messages,
            allow_change_subject=allow_change_subject,
            enable_logging=enable_logging,
            max_history_fetch=max_history_fetch,
            max_users=max_users,
            password_protected=password_protected,
            public=public,
            room_admins=room_admins,
            room_owners=room_owners,
            password=password,
            language=language,
            timeout=timeout,
        )

    @action
    def set_nick(
        self,
        room_id: str,
        nick: str,
        timeout: Optional[float] = XmppBaseMixin.DEFAULT_TIMEOUT,
    ):
        """
        Set the nick of the user on a specific room.

        :param room_id: The target room JID.
        :param nick: New nick.
        :param timeout: Request timeout (default: 20 seconds). Set to null for
            no timeout.
        """
        self._async_run(
            self._room_handler.set_nick,
            room_id=room_id,
            nick=nick,
            timeout=timeout,
        )

    @action
    def add_user(self, user_id: str):
        """
        Add the specified user ID to the roster.

        :param user_id: The Jabber ID of the user to add.
        """
        self._roster_handler.add_user(user_id)

    @action
    def remove_user(self, user_id: str):
        """
        Remove the specified user ID from the roster.

        :param user_id: The Jabber ID of the user to remove.
        """
        self._roster_handler.remove_user(user_id)

    @action
    def request_voice(
        self, room_id: str, timeout: Optional[float] = XmppBaseMixin.DEFAULT_TIMEOUT
    ):
        """
        Request voice (i.e. participant role) in a room.

        :param room_id: The Jabber ID of the room.
        :param timeout: Request timeout (default: 20 seconds). Set to null for
            no timeout.
        """
        self._async_run(
            self._room_handler.request_voice, room_id=room_id, timeout=timeout
        )

    @action
    def status(self):
        """
        Get the current status of the client.

        :return:

            .. code-block:: python

                {
                  # List of pending room invites, as Jabber IDs
                  "room_invites": ["bar@conference.xmpp.example.org"],

                  # List of pending user invites, as Jabber IDs
                  "user_invites": ["ignore-me@example.org"],

                  # List of users the client is subscribed to
                  "users": [
                    "buddy@example.org"
                  ],

                  # Map of rooms the client has joined, indexed by room ID
                  "rooms": {
                    "tests@conference.xmpp.manganiello.tech": {
                      "room_id": "foo@conference.xmpp.example.org",
                      "joined": true,
                      # Possible values:
                      # ACTIVE, DISCONNECTED, HISTORY, JOIN_PRESENCE
                      "state": "ACTIVE",
                      "nick": "me",

                      # Map of room members, indexed by user ID
                      "members": {
                        "me@example.org": {
                          "user_id": "me@example.org",
                          "nick": "me",
                          # Possible affiliation values:
                          # none, member, outcast, owner, publisher, publish-only
                          "affiliation": "none",

                          # Possible role values:
                          # none, participant, visitor, moderator
                          "role": "participant",
                          "is_self": true,
                          "available": true,

                          # Possible state values:
                          # available, offline, away, xa, chat, dnd
                          "state": "available"
                        },

                        "buddy@example.org": {
                          "user_id": "buddy@example.org",
                          "nick": "SomeBuddy",
                          "affiliation": "owner",
                          "role": "moderator",
                          "is_self": false,
                          "available": true,
                          "state": "away"
                        }
                      }
                    }
                  }
                }

        """
        return self._state.asdict(return_passwords=False)


# vim:sw=4:ts=4:et:
