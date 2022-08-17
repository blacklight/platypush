import asyncio
import datetime
import json
import logging
import os
import pathlib
import re

from dataclasses import dataclass
from typing import Coroutine

from async_lru import alru_cache
from nio import (
    AsyncClient,
    AsyncClientConfig,
    CallAnswerEvent,
    CallHangupEvent,
    CallInviteEvent,
    DevicesError,
    Event,
    InviteNameEvent,
    JoinedRoomsError,
    KeyVerificationStart,
    KeyVerificationAccept,
    KeyVerificationMac,
    KeyVerificationKey,
    KeyVerificationCancel,
    LocalProtocolError,
    LoginResponse,
    MatrixRoom,
    MegolmEvent,
    ProfileGetResponse,
    RoomCreateEvent,
    RoomGetEventError,
    RoomGetStateError,
    RoomGetStateResponse,
    RoomMemberEvent,
    RoomMessageText,
    RoomMessageMedia,
    RoomTopicEvent,
    RoomUpgradeEvent,
    StickerEvent,
    ToDeviceError,
    UnknownEncryptedEvent,
    UnknownEvent,
)

from nio.client.async_client import client_session
from nio.exceptions import OlmUnverifiedDeviceError

from platypush.config import Config
from platypush.context import get_bus
from platypush.message.event.matrix import (
    MatrixCallAnswerEvent,
    MatrixCallHangupEvent,
    MatrixCallInviteEvent,
    MatrixEncryptedMessageEvent,
    MatrixMediaMessageEvent,
    MatrixMessageEvent,
    MatrixReactionEvent,
    MatrixRoomCreatedEvent,
    MatrixRoomInviteEvent,
    MatrixRoomJoinEvent,
    MatrixRoomLeaveEvent,
    MatrixRoomTopicChangedEvent,
    MatrixStickerEvent,
)

from platypush.plugins import AsyncRunnablePlugin, action
from platypush.schemas.matrix import (
    MatrixDeviceSchema,
    MatrixEventIdSchema,
    MatrixProfileSchema,
    MatrixRoomSchema,
)

logger = logging.getLogger(__name__)


@dataclass
class Credentials:
    server_url: str
    user_id: str
    access_token: str
    device_id: str | None

    def to_dict(self) -> dict:
        return {
            'server_url': self.server_url,
            'user_id': self.user_id,
            'access_token': self.access_token,
            'device_id': self.device_id,
        }


class MatrixClient(AsyncClient):
    def __init__(
        self,
        *args,
        credentials_file: str,
        store_path: str | None = None,
        config: AsyncClientConfig | None = None,
        autojoin_on_invite=True,
        **kwargs,
    ):
        credentials_file = os.path.abspath(os.path.expanduser(credentials_file))

        if not store_path:
            store_path = os.path.join(Config.get('workdir'), 'matrix', 'store')  # type: ignore
        if store_path:
            store_path = os.path.abspath(os.path.expanduser(store_path))
            pathlib.Path(store_path).mkdir(exist_ok=True, parents=True)
        if not config:
            config = AsyncClientConfig(
                max_limit_exceeded=0,
                max_timeouts=0,
                store_sync_tokens=True,
                encryption_enabled=True,
            )

        super().__init__(*args, config=config, store_path=store_path, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
        self._credentials_file = credentials_file
        self._autojoin_on_invite = autojoin_on_invite
        self._first_sync_performed = asyncio.Event()

    async def _autojoin_room_callback(self, room: MatrixRoom, *_):
        await self.join(room.room_id)  # type: ignore

    def _load_from_file(self):
        if not os.path.isfile(self._credentials_file):
            return

        try:
            with open(self._credentials_file, 'r') as f:
                credentials = json.load(f)
        except json.JSONDecodeError:
            self.logger.warning(
                'Could not read credentials_file %s - overwriting it',
                self._credentials_file,
            )
            return

        assert credentials.get('user_id'), 'Missing user_id'
        assert credentials.get('access_token'), 'Missing access_token'

        self.access_token = credentials['access_token']
        self.user_id = credentials['user_id']
        self.homeserver = credentials.get('server_url', self.homeserver)
        if credentials.get('device_id'):
            self.device_id = credentials['device_id']

        self.load_store()

    async def login(
        self,
        password: str | None = None,
        device_name: str | None = None,
        token: str | None = None,
    ) -> LoginResponse:
        self._load_from_file()
        login_res = None

        if self.access_token:
            self.load_store()
            self.logger.info(
                'Logged in to %s as %s using the stored access token',
                self.homeserver,
                self.user_id,
            )

            login_res = LoginResponse(
                user_id=self.user_id,
                device_id=self.device_id,
                access_token=self.access_token,
            )
        else:
            assert self.user, 'No credentials file found and no user provided'
            login_args = {'device_name': device_name}
            if token:
                login_args['token'] = token
            else:
                assert (
                    password
                ), 'No credentials file found and no password nor access token provided'
                login_args['password'] = password

            login_res = await super().login(**login_args)
            assert isinstance(login_res, LoginResponse), f'Failed to login: {login_res}'
            self.logger.info(login_res)

            credentials = Credentials(
                server_url=self.homeserver,
                user_id=login_res.user_id,
                access_token=login_res.access_token,
                device_id=login_res.device_id,
            )

            with open(self._credentials_file, 'w') as f:
                json.dump(credentials.to_dict(), f)
            os.chmod(self._credentials_file, 0o600)

        if self.should_upload_keys:
            self.logger.info('Uploading encryption keys')
            await self.keys_upload()

        self.logger.info('Synchronizing rooms')
        self._first_sync_performed.clear()
        sync_token = self.loaded_sync_token
        self.loaded_sync_token = ''
        await self.sync(sync_filter={'room': {'timeline': {'limit': 1}}})
        self._add_callbacks()

        self.loaded_sync_token = sync_token
        self._first_sync_performed.set()
        self.logger.info('Rooms synchronized')
        return login_res

    def _add_callbacks(self):
        self.add_event_callback(self._event_catch_all, Event)
        self.add_event_callback(self._on_invite, InviteNameEvent)  # type: ignore
        self.add_event_callback(self._on_room_message, RoomMessageText)  # type: ignore
        self.add_event_callback(self._on_media_message, RoomMessageMedia)  # type: ignore
        self.add_event_callback(self._on_room_member, RoomMemberEvent)  # type: ignore
        self.add_event_callback(self._on_room_topic_changed, RoomTopicEvent)  # type: ignore
        self.add_event_callback(self._on_call_invite, CallInviteEvent)  # type: ignore
        self.add_event_callback(self._on_call_answer, CallAnswerEvent)  # type: ignore
        self.add_event_callback(self._on_call_hangup, CallHangupEvent)  # type: ignore
        self.add_event_callback(self._on_sticker_message, StickerEvent)  # type: ignore
        self.add_event_callback(self._on_unknown_event, UnknownEvent)  # type: ignore
        self.add_event_callback(self._on_unknown_encrypted_event, UnknownEncryptedEvent)  # type: ignore
        self.add_event_callback(self._on_unknown_encrypted_event, MegolmEvent)  # type: ignore
        self.add_to_device_callback(self._on_key_verification_start, KeyVerificationStart)  # type: ignore
        self.add_to_device_callback(self._on_key_verification_cancel, KeyVerificationCancel)  # type: ignore
        self.add_to_device_callback(self._on_key_verification_key, KeyVerificationKey)  # type: ignore
        self.add_to_device_callback(self._on_key_verification_mac, KeyVerificationMac)  # type: ignore
        self.add_to_device_callback(self._on_key_verification_accept, KeyVerificationAccept)  # type: ignore

        if self._autojoin_on_invite:
            self.add_event_callback(self._autojoin_room_callback, InviteNameEvent)  # type: ignore

    @alru_cache(maxsize=500)
    @client_session
    async def get_profile(self, user_id: str | None = None) -> ProfileGetResponse:
        """
        Cached version of get_profile.
        """
        ret = await super().get_profile(user_id)
        assert isinstance(
            ret, ProfileGetResponse
        ), f'Could not retrieve profile for user {user_id}: {ret.message}'
        return ret

    @alru_cache(maxsize=500)
    @client_session
    async def room_get_state(self, room_id: str) -> RoomGetStateResponse:
        """
        Cached version of room_get_state.
        """
        ret = await super().room_get_state(room_id)
        assert isinstance(
            ret, RoomGetStateResponse
        ), f'Could not retrieve profile for room {room_id}: {ret.message}'
        return ret

    async def _event_base_args(
        self, room: MatrixRoom, event: Event | None = None
    ) -> dict:
        sender_id = event.sender if event else None
        sender = (
            await self.get_profile(sender_id) if sender_id else None  # type: ignore
        )

        return {
            'server_url': self.homeserver,
            'sender_id': sender_id,
            'sender_display_name': sender.displayname if sender else None,
            'sender_avatar_url': sender.avatar_url if sender else None,
            'room_id': room.room_id,
            'room_name': room.name,
            'room_topic': room.topic,
            'server_timestamp': (
                datetime.datetime.fromtimestamp(event.server_timestamp / 1000)
                if event and getattr(event, 'server_timestamp', None)
                else None
            ),
        }

    async def _event_catch_all(self, room: MatrixRoom, event: Event):
        self.logger.debug('Received event on room %s: %r', room.room_id, event)

    async def _on_invite(self, room: MatrixRoom, event: RoomMessageText):
        get_bus().post(
            MatrixRoomInviteEvent(
                **(await self._event_base_args(room, event)),
            )
        )

    async def _on_room_message(self, room: MatrixRoom, event: RoomMessageText):
        if self._first_sync_performed.is_set():
            get_bus().post(
                MatrixMessageEvent(
                    **(await self._event_base_args(room, event)),
                    body=event.body,
                )
            )

    async def _on_room_member(self, room: MatrixRoom, event: RoomMemberEvent):
        evt_type = None
        if event.membership == 'join':
            evt_type = MatrixRoomJoinEvent
        elif event.membership == 'leave':
            evt_type = MatrixRoomLeaveEvent

        if evt_type and self._first_sync_performed.is_set():
            get_bus().post(
                evt_type(
                    **(await self._event_base_args(room, event)),
                )
            )

    async def _on_room_topic_changed(self, room: MatrixRoom, event: RoomTopicEvent):
        if self._first_sync_performed.is_set():
            get_bus().post(
                MatrixRoomTopicChangedEvent(
                    **(await self._event_base_args(room, event)),
                    topic=event.topic,
                )
            )

    async def _on_call_invite(self, room: MatrixRoom, event: CallInviteEvent):
        if self._first_sync_performed.is_set():
            get_bus().post(
                MatrixCallInviteEvent(
                    call_id=event.call_id,
                    version=event.version,
                    invite_validity=event.lifetime / 1000.0,
                    sdp=event.offer.get('sdp'),
                    **(await self._event_base_args(room, event)),
                )
            )

    async def _on_call_answer(self, room: MatrixRoom, event: CallAnswerEvent):
        if self._first_sync_performed.is_set():
            get_bus().post(
                MatrixCallAnswerEvent(
                    call_id=event.call_id,
                    version=event.version,
                    sdp=event.answer.get('sdp'),
                    **(await self._event_base_args(room, event)),
                )
            )

    async def _on_call_hangup(self, room: MatrixRoom, event: CallHangupEvent):
        if self._first_sync_performed.is_set():
            get_bus().post(
                MatrixCallHangupEvent(
                    call_id=event.call_id,
                    version=event.version,
                    **(await self._event_base_args(room, event)),
                )
            )

    async def _on_room_created(self, room: MatrixRoom, event: RoomCreateEvent):
        get_bus().post(
            MatrixRoomCreatedEvent(
                **(await self._event_base_args(room, event)),
            )
        )

    async def _on_media_message(self, room: MatrixRoom, event: RoomMessageMedia):
        if self._first_sync_performed.is_set():
            get_bus().post(
                MatrixMediaMessageEvent(
                    url=event.url,
                    **(await self._event_base_args(room, event)),
                )
            )

    async def _on_sticker_message(self, room: MatrixRoom, event: StickerEvent):
        if self._first_sync_performed.is_set():
            get_bus().post(
                MatrixStickerEvent(
                    url=event.url,
                    **(await self._event_base_args(room, event)),
                )
            )

    async def _on_key_verification_start(self, event: KeyVerificationStart):
        assert self.olm, 'OLM state machine not initialized'
        self.olm.handle_key_verification(event)
        self.logger.info(f'Received a key verification request from {event.sender}')

        if 'emoji' not in event.short_authentication_string:
            self.logger.warning(
                'Only emoji verification is supported, but the verifying device '
                'provided the following authentication methods: %r',
                event.short_authentication_string,
            )
            return

        rs = await self.accept_key_verification(event.transaction_id)
        assert not isinstance(
            rs, ToDeviceError
        ), f'accept_key_verification failed: {rs}'

        sas = self.key_verifications[event.transaction_id]
        rs = await self.to_device(sas.share_key())
        assert not isinstance(rs, ToDeviceError), f'Shared key exchange failed: {rs}'

    async def _on_key_verification_accept(self, event: KeyVerificationAccept):
        self.logger.info('Key verification from device %s accepted', event.sender)

    async def _on_key_verification_cancel(self, event: KeyVerificationCancel):
        self.logger.info(
            'The device %s cancelled a key verification request. ' 'Reason: %s',
            event.sender,
            event.reason,
        )

    async def _on_key_verification_key(self, event: KeyVerificationKey):
        sas = self.key_verifications[event.transaction_id]
        self.logger.info(
            'Received emoji verification from device %s: %s',
            event.sender,
            sas.get_emoji(),
        )

        # TODO Support user interaction instead of blindly confirming?
        # await asyncio.sleep(5)
        print('***** SENDING AUTH STRING')
        rs = await self.confirm_short_auth_string(event.transaction_id)
        assert not isinstance(
            rs, ToDeviceError
        ), f'confirm_short_auth_string failed: {rs}'

    async def _on_key_verification_mac(self, event: KeyVerificationMac):
        self.logger.info('Received MAC verification request from %s', event.sender)
        sas = self.key_verifications[event.transaction_id]

        try:
            mac = sas.get_mac()
        except LocalProtocolError as e:
            self.logger.warning(
                'Verification from %s cancelled or unexpected protocol error. '
                'Reason: %s',
                e,
                event.sender,
            )
            return

        rs = await self.to_device(mac)
        assert not isinstance(
            rs, ToDeviceError
        ), f'Sending of the verification MAC to {event.sender} failed: {rs}'

        self.logger.info('This device has been successfully verified!')

    async def _on_room_upgrade(self, room: MatrixRoom, event: RoomUpgradeEvent):
        self.logger.info(
            'The room %s has been moved to %s', room.room_id, event.replacement_room
        )

        await self.room_leave(room.room_id)
        await self.join(event.replacement_room)

    async def _on_unknown_encrypted_event(
        self, room: MatrixRoom, event: UnknownEncryptedEvent | MegolmEvent
    ):
        body = getattr(event, 'ciphertext', '')
        get_bus().post(
            MatrixEncryptedMessageEvent(
                body=body,
                **(await self._event_base_args(room, event)),
            )
        )

    async def _on_unknown_event(self, room: MatrixRoom, event: UnknownEvent):
        evt = None

        if event.type == 'm.reaction' and self._first_sync_performed.is_set():
            # Get the ID of the event this was a reaction to
            relation_dict = event.source.get('content', {}).get('m.relates_to', {})
            reacted_to = relation_dict.get('event_id')
            if reacted_to and relation_dict.get('rel_type') == 'm.annotation':
                event_response = await self.room_get_event(room.room_id, reacted_to)

                if isinstance(event_response, RoomGetEventError):
                    self.logger.warning(
                        'Error getting event that was reacted to (%s)', reacted_to
                    )
                else:
                    evt = MatrixReactionEvent(
                        in_response_to_event_id=event_response.event.event_id,
                        **(await self._event_base_args(room, event)),
                    )

        if evt:
            get_bus().post(evt)
        else:
            self.logger.info(
                'Received an unknown event on room %s: %r', room.room_id, event
            )


class MatrixPlugin(AsyncRunnablePlugin):
    """
    Matrix chat integration.

    Requires:

        * **matrix-nio** (``pip install 'matrix-nio[e2e]'``)
        * **libolm** (on Debian ```apt-get install libolm-devel``, on Arch
            ``pacman -S libolm``)
        * **async_lru** (``pip install async_lru``)

    Note that ``libolm`` and the ``[e2e]`` module are only required if you want E2E encryption
    support.

    Triggers:

        * :class:`platypush.message.event.matrix.MatrixMessageEvent`: when a message is received.
        * :class:`platypush.message.event.matrix.MatrixMediaMessageEvent`: when a media message is received.
        * :class:`platypush.message.event.matrix.MatrixRoomCreatedEvent`: when a room is created.
        * :class:`platypush.message.event.matrix.MatrixRoomJoinEvent`: when a user joins a room.
        * :class:`platypush.message.event.matrix.MatrixRoomLeaveEvent`: when a user leaves a room.
        * :class:`platypush.message.event.matrix.MatrixRoomInviteEvent`: when the user is invited to a room.
        * :class:`platypush.message.event.matrix.MatrixRoomTopicChangedEvent`: when the topic/title of a room changes.
        * :class:`platypush.message.event.matrix.MatrixCallInviteEvent`: when the user is invited to a call.
        * :class:`platypush.message.event.matrix.MatrixCallAnswerEvent`: when a called user wishes to pick the call.
        * :class:`platypush.message.event.matrix.MatrixCallHangupEvent`: when a called user exits the call.
        * :class:`platypush.message.event.matrix.MatrixStickerEvent`: when a sticker is sent to a room.
        * :class:`platypush.message.event.matrix.MatrixEncryptedMessageEvent`: when a message is received but the
            client doesn't have the E2E keys to decrypt it, or encryption has not been enabled.

    """

    def __init__(
        self,
        server_url: str = 'https://matrix.to',
        user_id: str | None = None,
        password: str | None = None,
        access_token: str | None = None,
        device_name: str | None = 'platypush',
        device_id: str | None = None,
        autojoin_on_invite: bool = True,
        **kwargs,
    ):
        """
        Authentication requires user_id/password on the first login.
        Afterwards, session credentials are stored under
        ``<$PLATYPUSH_WORKDIR>/matrix/credentials.json`` (default:
        ``~/.local/share/platypush/matrix/credentials.json``), and you can
        remove the cleartext credentials from your configuration file.

        Otherwise, if you already have an ``access_token``, you can set the
        associated field instead of using ``password``. This may be required if
        the user has 2FA enabled.

        :param server_url: Default Matrix instance base URL (default: ``https://matrix.to``).
        :param user_id: user_id, in the format ``@user:example.org``, or just the username if the
            account is hosted on the same server configured in the ``server_url``.
        :param password: User password.
        :param access_token: User access token.
        :param device_name: The name of this device/connection (default: ``platypush``).
        :param device_id: Use an existing ``device_id`` for the sessions.
        :param autojoin_on_invite: Whether the account should automatically join rooms
            upon invite. If false, then you may want to implement your own
            logic in an event hook when a :class:`platypush.message.event.matrix.MatrixRoomInviteEvent`
            event is received, and call the :meth:`.join` method if required.
        """
        super().__init__(**kwargs)
        if not (server_url.startswith('http://') or server_url.startswith('https://')):
            server_url = f'https://{server_url}'
        self._server_url = server_url
        server_name = self._server_url.split('/')[2].split(':')[0]

        if user_id and not re.match(user_id, '^@[a-zA-Z0-9.-_]+:.+'):
            user_id = f'@{user_id}:{server_name}'

        # self._matrix_proc: multiprocessing.Process | None = None
        self._user_id = user_id
        self._password = password
        self._access_token = access_token
        self._device_name = device_name
        self._device_id = device_id
        self._autojoin_on_invite = autojoin_on_invite
        self._workdir = os.path.join(Config.get('workdir'), 'matrix')  # type: ignore
        self._credentials_file = os.path.join(self._workdir, 'credentials.json')
        self._processed_responses = {}
        self._client = self._get_client()
        pathlib.Path(self._workdir).mkdir(parents=True, exist_ok=True)

    def _get_client(self) -> AsyncClient:
        return MatrixClient(
            homeserver=self._server_url,
            user=self._user_id,
            credentials_file=self._credentials_file,
            autojoin_on_invite=self._autojoin_on_invite,
            device_id=self._device_id,
        )

    async def _login(self) -> AsyncClient:
        if not self._client:
            self._client = self._get_client()

        await self._client.login(
            password=self._password,
            device_name=self._device_name,
            token=self._access_token,
        )

        return self._client

    async def listen(self):
        while not self.should_stop():
            await self._login()
            assert self._client

            try:
                await self._client.sync_forever(timeout=30000, full_state=True)
            except KeyboardInterrupt:
                pass
            finally:
                try:
                    await self._client.close()
                finally:
                    self._client = None

    def _loop_execute(self, coro: Coroutine):
        assert self._loop, 'The loop is not running'
        try:
            ret = asyncio.run_coroutine_threadsafe(coro, self._loop).result()
        except OlmUnverifiedDeviceError as e:
            raise AssertionError(str(e))

        if hasattr(ret, 'transport_response'):
            response = ret.transport_response
            assert response.ok, f'{coro} failed with status {response.status}'

        return ret

    @action
    def send_message(
        self,
        room_id: str,
        message_type: str = 'text',
        body: str | None = None,
        tx_id: str | None = None,
        ignore_unverified_devices: bool = False,
    ):
        """
        Send a message to a room.

        :param room_id: Room ID.
        :param body: Message body.
        :param message_type: Message type. Supported: `text`, `audio`, `video`,
            `image`. Default: `text`.
        :param tx_id: Unique transaction ID to associate to this message.
        :param ignore_unverified_devices: If true, unverified devices will be
            ignored (default: False).
        :return: .. schema:: matrix.MatrixEventIdSchema
        """
        assert self._client, 'Client not connected'
        assert self._loop, 'The loop is not running'

        ret = self._loop_execute(
            self._client.room_send(
                message_type='m.' + message_type,
                room_id=room_id,
                tx_id=tx_id,
                ignore_unverified_devices=ignore_unverified_devices,
                content={
                    'body': body,
                },
            )
        )

        ret = asyncio.run_coroutine_threadsafe(
            ret.transport_response.json(), self._loop
        ).result()

        return MatrixEventIdSchema().dump(ret)

    @action
    def get_profile(self, user_id: str):
        """
        Retrieve the details about a user.

        :param user_id: User ID.
        :return: .. schema:: matrix.MatrixProfileSchema
        """
        assert self._client, 'Client not connected'
        profile = self._loop_execute(self._client.get_profile(user_id))
        profile.user_id = user_id
        return MatrixProfileSchema().dump(profile)

    @action
    def get_room(self, room_id: str):
        """
        Retrieve the details about a room.

        :param room_id: room ID.
        :return: .. schema:: matrix.MatrixRoomSchema
        """
        assert self._client, 'Client not connected'
        response = self._loop_execute(self._client.room_get_state(room_id))
        assert not isinstance(response, RoomGetStateError), response.message

        room_args = {'room_id': room_id, 'own_user_id': None, 'encrypted': False}
        room_params = {}

        for evt in response.events:
            if evt.get('type') == 'm.room.create':
                room_args['own_user_id'] = evt.get('content', {}).get('creator')
            elif evt.get('type') == 'm.room.encryption':
                room_args['encrypted'] = False
            elif evt.get('type') == 'm.room.name':
                room_params['name'] = evt.get('content', {}).get('name')
            elif evt.get('type') == 'm.room.topic':
                room_params['topic'] = evt.get('content', {}).get('topic')

        room = MatrixRoom(**room_args)
        for k, v in room_params.items():
            setattr(room, k, v)
        return MatrixRoomSchema().dump(room)

    @action
    def get_devices(self):
        """
        Get the list of devices associated to the current user.

        :return: .. schema:: matrix.MatrixDeviceSchema(many=True)
        """
        assert self._client, 'Client not connected'
        response = self._loop_execute(self._client.devices())
        assert not isinstance(response, DevicesError), response.message
        return MatrixDeviceSchema().dump(response.devices, many=True)

    @action
    def get_joined_rooms(self):
        """
        Retrieve the rooms that the user has joined.
        """
        assert self._client, 'Client not connected'
        response = self._loop_execute(self._client.joined_rooms())
        assert not isinstance(response, JoinedRoomsError), response.message

        return [self.get_room(room_id).output for room_id in response.rooms]  # type: ignore

    @action
    def upload_keys(self):
        """
        Synchronize the E2EE keys with the homeserver.
        """
        assert self._client, 'Client not connected'
        self._loop_execute(self._client.keys_upload())


# vim:sw=4:ts=4:et:
