import asyncio
import datetime
import json
import logging
import os
import pathlib
import re
import threading

from dataclasses import dataclass
from typing import Collection, Coroutine, Dict
from urllib.parse import urlparse

from async_lru import alru_cache
from nio import (
    Api,
    AsyncClient,
    AsyncClientConfig,
    CallAnswerEvent,
    CallHangupEvent,
    CallInviteEvent,
    ErrorResponse,
    Event,
    InviteEvent,
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
    RoomEncryptedAudio,
    RoomEncryptedFile,
    RoomEncryptedImage,
    RoomEncryptedMedia,
    RoomEncryptedVideo,
    RoomGetEventError,
    RoomGetStateResponse,
    RoomMemberEvent,
    RoomMessageAudio,
    RoomMessageFile,
    RoomMessageFormatted,
    RoomMessageText,
    RoomMessageImage,
    RoomMessageMedia,
    RoomMessageVideo,
    RoomTopicEvent,
    RoomUpgradeEvent,
    StickerEvent,
    ToDeviceError,
    UnknownEncryptedEvent,
    UnknownEvent,
)

import aiofiles
import aiofiles.os

from nio.client.async_client import client_session
from nio.crypto import decrypt_attachment
from nio.crypto.device import OlmDevice
from nio.exceptions import OlmUnverifiedDeviceError
from nio.responses import DownloadResponse

from platypush.config import Config
from platypush.context import get_bus
from platypush.message.event.matrix import (
    MatrixCallAnswerEvent,
    MatrixCallHangupEvent,
    MatrixCallInviteEvent,
    MatrixEncryptedMessageEvent,
    MatrixMessageAudioEvent,
    MatrixMessageEvent,
    MatrixMessageFileEvent,
    MatrixMessageImageEvent,
    MatrixMessageVideoEvent,
    MatrixReactionEvent,
    MatrixRoomCreatedEvent,
    MatrixRoomInviteEvent,
    MatrixRoomJoinEvent,
    MatrixRoomLeaveEvent,
    MatrixRoomTopicChangedEvent,
    MatrixSyncEvent,
)

from platypush.plugins import AsyncRunnablePlugin, action
from platypush.schemas.matrix import (
    MatrixDeviceSchema,
    MatrixDownloadedFileSchema,
    MatrixEventIdSchema,
    MatrixMyDeviceSchema,
    MatrixProfileSchema,
    MatrixRoomSchema,
)

from platypush.utils import get_mime_type

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
        autotrust_devices=False,
        autotrust_devices_whitelist: Collection[str] | None = None,
        autotrust_rooms_whitelist: Collection[str] | None = None,
        autotrust_users_whitelist: Collection[str] | None = None,
        **kwargs,
    ):
        credentials_file = os.path.abspath(os.path.expanduser(credentials_file))

        if not store_path:
            store_path = os.path.join(Config.get('workdir'), 'matrix', 'store')  # type: ignore

        assert store_path
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
        self._autotrust_devices = autotrust_devices
        self._autotrust_devices_whitelist = autotrust_devices_whitelist
        self._autotrust_rooms_whitelist = autotrust_rooms_whitelist or set()
        self._autotrust_users_whitelist = autotrust_users_whitelist or set()
        self._first_sync_performed = asyncio.Event()

        self._encrypted_attachments_keystore_path = os.path.join(
            store_path, 'attachment_keys.json'
        )
        self._encrypted_attachments_keystore = {}
        self._sync_store_timer: threading.Timer | None = None
        keystore = {}

        try:
            with open(self._encrypted_attachments_keystore_path, 'r') as f:
                keystore = json.load(f)
        except (ValueError, OSError):
            with open(self._encrypted_attachments_keystore_path, 'w') as f:
                f.write(json.dumps({}))

        pathlib.Path(self._encrypted_attachments_keystore_path).touch(
            mode=0o600, exist_ok=True
        )
        self._encrypted_attachments_keystore = {
            tuple(key.split('|')): data for key, data in keystore.items()
        }

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

        self.logger.info('Synchronizing state')
        self._first_sync_performed.clear()
        self._add_callbacks()
        sync_token = self.loaded_sync_token
        self.loaded_sync_token = ''
        await self.sync(sync_filter={'room': {'timeline': {'limit': 1}}})
        self.loaded_sync_token = sync_token

        self._sync_devices_trust()
        self._first_sync_performed.set()

        get_bus().post(MatrixSyncEvent(server_url=self.homeserver))
        self.logger.info('State synchronized')
        return login_res

    def _sync_devices_trust(self):
        all_devices = self.get_devices()
        devices_to_trust: Dict[str, OlmDevice] = {}
        untrusted_devices = {
            device_id: device
            for device_id, device in all_devices.items()
            if not device.verified
        }

        if self._autotrust_devices:
            devices_to_trust.update(untrusted_devices)
        else:
            if self._autotrust_devices_whitelist:
                devices_to_trust.update(
                    {
                        device_id: device
                        for device_id, device in all_devices.items()
                        if device_id in self._autotrust_devices_whitelist
                        and device_id in untrusted_devices
                    }
                )
            if self._autotrust_rooms_whitelist:
                devices_to_trust.update(
                    {
                        device_id: device
                        for room_id, devices in self.get_devices_by_room().items()
                        for device_id, device in devices.items()  # type: ignore
                        if room_id in self._autotrust_rooms_whitelist
                        and device_id in untrusted_devices
                    }
                )
            if self._autotrust_users_whitelist:
                devices_to_trust.update(
                    {
                        device_id: device
                        for user_id, devices in self.get_devices_by_user().items()
                        for device_id, device in devices.items()  # type: ignore
                        if user_id in self._autotrust_users_whitelist
                        and device_id in untrusted_devices
                    }
                )

        for device in devices_to_trust.values():
            self.verify_device(device)
            self.logger.info(
                'Device %s by user %s added to the whitelist', device.id, device.user_id
            )

    def get_devices_by_user(
        self, user_id: str | None = None
    ) -> Dict[str, Dict[str, OlmDevice]] | Dict[str, OlmDevice]:
        devices = {user: devices for user, devices in self.device_store.items()}

        if user_id:
            devices = devices.get(user_id, {})
        return devices

    def get_devices(self) -> Dict[str, OlmDevice]:
        return {
            device_id: device
            for _, devices in self.device_store.items()
            for device_id, device in devices.items()
        }

    def get_device(self, device_id: str) -> OlmDevice | None:
        return self.get_devices().get(device_id)

    def get_devices_by_room(
        self, room_id: str | None = None
    ) -> Dict[str, Dict[str, OlmDevice]] | Dict[str, OlmDevice]:
        devices = {
            room_id: {
                device_id: device
                for _, devices in self.room_devices(room_id).items()
                for device_id, device in devices.items()
            }
            for room_id in self.rooms.keys()
        }

        if room_id:
            devices = devices.get(room_id, {})
        return devices

    def _add_callbacks(self):
        self.add_event_callback(self._event_catch_all, Event)
        self.add_event_callback(self._on_invite, InviteEvent)  # type: ignore
        self.add_event_callback(self._on_message, RoomMessageText)  # type: ignore
        self.add_event_callback(self._on_message, RoomMessageMedia)  # type: ignore
        self.add_event_callback(self._on_message, RoomEncryptedMedia)  # type: ignore
        self.add_event_callback(self._on_message, StickerEvent)  # type: ignore
        self.add_event_callback(self._on_room_member, RoomMemberEvent)  # type: ignore
        self.add_event_callback(self._on_room_topic_changed, RoomTopicEvent)  # type: ignore
        self.add_event_callback(self._on_call_invite, CallInviteEvent)  # type: ignore
        self.add_event_callback(self._on_call_answer, CallAnswerEvent)  # type: ignore
        self.add_event_callback(self._on_call_hangup, CallHangupEvent)  # type: ignore
        self.add_event_callback(self._on_unknown_event, UnknownEvent)  # type: ignore
        self.add_event_callback(self._on_unknown_encrypted_event, UnknownEncryptedEvent)  # type: ignore
        self.add_event_callback(self._on_unknown_encrypted_event, MegolmEvent)  # type: ignore
        self.add_to_device_callback(self._on_key_verification_start, KeyVerificationStart)  # type: ignore
        self.add_to_device_callback(self._on_key_verification_cancel, KeyVerificationCancel)  # type: ignore
        self.add_to_device_callback(self._on_key_verification_key, KeyVerificationKey)  # type: ignore
        self.add_to_device_callback(self._on_key_verification_mac, KeyVerificationMac)  # type: ignore
        self.add_to_device_callback(self._on_key_verification_accept, KeyVerificationAccept)  # type: ignore

        if self._autojoin_on_invite:
            self.add_event_callback(self._autojoin_room_callback, InviteEvent)  # type: ignore

    def _sync_store(self):
        self.logger.info('Synchronizing keystore')
        serialized_keystore = json.dumps(
            {
                f'{server}|{media_id}': data
                for (
                    server,
                    media_id,
                ), data in self._encrypted_attachments_keystore.items()
            }
        )

        try:
            with open(self._encrypted_attachments_keystore_path, 'w') as f:
                f.write(serialized_keystore)
        finally:
            self._sync_store_timer = None

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

    async def download(
        self,
        server_name: str,
        media_id: str,
        filename: str | None = None,
        allow_remote: bool = True,
    ):
        response = await super().download(
            server_name, media_id, filename, allow_remote=allow_remote
        )

        assert isinstance(
            response, DownloadResponse
        ), f'Could not download media {media_id}: {response}'

        encryption_data = self._encrypted_attachments_keystore.get(
            (server_name, media_id)
        )
        if encryption_data:
            self.logger.info('Decrypting media %s using the available keys', media_id)
            response.filename = encryption_data.get('body', response.filename)
            response.content_type = encryption_data.get(
                'mimetype', response.content_type
            )
            response.body = decrypt_attachment(
                response.body,
                key=encryption_data.get('key'),
                hash=encryption_data.get('hash'),
                iv=encryption_data.get('iv'),
            )

        return response

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

    async def _on_message(
        self,
        room: MatrixRoom,
        event: RoomMessageText | RoomMessageMedia | RoomEncryptedMedia | StickerEvent,
    ):
        if self._first_sync_performed.is_set():
            evt_type = MatrixMessageEvent
            evt_args = {
                'body': event.body,
                'url': getattr(event, 'url', None),
                **(await self._event_base_args(room, event)),
            }

            if isinstance(event, (RoomMessageMedia, RoomEncryptedMedia, StickerEvent)):
                evt_args['url'] = event.url

            if isinstance(event, RoomEncryptedMedia):
                evt_args['thumbnail_url'] = event.thumbnail_url
                evt_args['mimetype'] = event.mimetype
                self._store_encrypted_media_keys(event)
            if isinstance(event, RoomMessageFormatted):
                evt_args['format'] = event.format
                evt_args['formatted_body'] = event.formatted_body

            if isinstance(event, (RoomMessageImage, RoomEncryptedImage)):
                evt_type = MatrixMessageImageEvent
            elif isinstance(event, (RoomMessageAudio, RoomEncryptedAudio)):
                evt_type = MatrixMessageAudioEvent
            elif isinstance(event, (RoomMessageVideo, RoomEncryptedVideo)):
                evt_type = MatrixMessageVideoEvent
            elif isinstance(event, (RoomMessageFile, RoomEncryptedFile)):
                evt_type = MatrixMessageFileEvent

            get_bus().post(evt_type(**evt_args))

    def _store_encrypted_media_keys(self, event: RoomEncryptedMedia):
        url = event.url.strip('/')
        parsed_url = urlparse(url)
        homeserver = parsed_url.netloc.strip('/')
        media_key = (homeserver, parsed_url.path.strip('/'))

        self._encrypted_attachments_keystore[media_key] = {
            'url': url,
            'body': event.body,
            'key': event.key['k'],
            'hash': event.hashes['sha256'],
            'iv': event.iv,
            'homeserver': homeserver,
            'mimetype': event.mimetype,
        }

        if not self._sync_store_timer:
            self._sync_store_timer = threading.Timer(5, self._sync_store)
            self._sync_store_timer.start()

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

    def _get_sas(self, event):
        sas = self.key_verifications.get(event.transaction_id)
        if not sas:
            self.logger.debug(
                'Received a key verification event with no associated transaction ID'
            )

        return sas

    async def _on_key_verification_start(self, event: KeyVerificationStart):
        self.logger.info(f'Received a key verification request from {event.sender}')

        if 'emoji' not in event.short_authentication_string:
            self.logger.warning(
                'Only emoji verification is supported, but the verifying device '
                'provided the following authentication methods: %r',
                event.short_authentication_string,
            )
            return

        sas = self._get_sas(event)
        if not sas:
            return

        rs = await self.accept_key_verification(sas.transaction_id)
        assert not isinstance(
            rs, ToDeviceError
        ), f'accept_key_verification failed: {rs}'

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
        sas = self._get_sas(event)
        if not sas:
            return

        self.logger.info(
            'Received emoji verification from device %s: %s',
            event.sender,
            sas.get_emoji(),
        )

        rs = await self.confirm_short_auth_string(sas.transaction_id)
        assert not isinstance(
            rs, ToDeviceError
        ), f'confirm_short_auth_string failed: {rs}'

    async def _on_key_verification_mac(self, event: KeyVerificationMac):
        self.logger.info('Received MAC verification request from %s', event.sender)
        sas = self._get_sas(event)
        if not sas:
            return

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

    async def upload_file(
        self,
        file: str,
        name: str | None = None,
        content_type: str | None = None,
        encrypt: bool = False,
    ):
        file = os.path.expanduser(file)
        file_stat = await aiofiles.os.stat(file)

        async with aiofiles.open(file, 'rb') as f:
            return await super().upload(
                f,  # type: ignore
                content_type=(
                    content_type or get_mime_type(file) or 'application/octet-stream'
                ),
                filename=name or os.path.basename(file),
                encrypt=encrypt,
                filesize=file_stat.st_size,
            )


class MatrixPlugin(AsyncRunnablePlugin):
    """
    Matrix chat integration.

    Requires:

        * **matrix-nio** (``pip install 'matrix-nio[e2e]'``)
        * **libolm** (on Debian ```apt-get install libolm-devel``, on Arch
            ``pacman -S libolm``)
        * **async_lru** (``pip install async_lru``)

    Note that ``libolm`` and the ``[e2e]`` module are only required if you want
    E2E encryption support.

    Unless you configure the extension to use the token of an existing trusted
    device, it is recommended that you mark the virtual device used by this
    integration as trusted through a device that is already trusted. You may
    encounter errors when sending or receiving messages on encrypted rooms if
    your user has some untrusted devices. The easiest way to mark the device as
    trusted is the following:

        - Configure the integration with your credentials and start Platypush.
        - Use the same credentials to log in through a Matrix app or web client
          (Element, Hydrogen, etc.) that has already been trusted.
        - You should see a notification that prompts you to review the
          untrusted devices logged in to your account. Dismiss it for now -
          that verification path is currently broken on the underlying library
          used by this integration.
        - Instead, select a room that you have already joined, select the list
          of users in the room and select yourself.
        - In the _Security_ section, you should see that at least one device is
          marked as unverified, and you can start the verification process by
          clicking on it.
        - Select "_Verify through emoji_". A list of emojis should be prompted.
          Optionally, verify the logs of the application to check that you see
          the same list. Then confirm that you see the same emojis, and your
          device will be automatically marked as trusted.

    All the URLs returned by actions and events on this plugin are in the
    ``mxc://<server>/<media_id>`` format. You can either convert them to HTTP
    through the :meth:`.mxc_to_http` method, or download them through the
    :meth:`.download` method.

    Triggers:

        * :class:`platypush.message.event.matrix.MatrixMessageEvent`: when a
            message is received.
        * :class:`platypush.message.event.matrix.MatrixMessageImageEvent`: when a
            message containing an image is received.
        * :class:`platypush.message.event.matrix.MatrixMessageAudioEvent`: when a
            message containing an audio file is received.
        * :class:`platypush.message.event.matrix.MatrixMessageVideoEvent`: when a
            message containing a video file is received.
        * :class:`platypush.message.event.matrix.MatrixMessageFileEvent`: when a
            message containing a generic file is received.
        * :class:`platypush.message.event.matrix.MatrixSyncEvent`: when the
            startup synchronization has been completed and the plugin is ready to
            use.
        * :class:`platypush.message.event.matrix.MatrixRoomCreatedEvent`: when
            a room is created.
        * :class:`platypush.message.event.matrix.MatrixRoomJoinEvent`: when a
            user joins a room.
        * :class:`platypush.message.event.matrix.MatrixRoomLeaveEvent`: when a
            user leaves a room.
        * :class:`platypush.message.event.matrix.MatrixRoomInviteEvent`: when
            the user is invited to a room.
        * :class:`platypush.message.event.matrix.MatrixRoomTopicChangedEvent`:
            when the topic/title of a room changes.
        * :class:`platypush.message.event.matrix.MatrixCallInviteEvent`: when
            the user is invited to a call.
        * :class:`platypush.message.event.matrix.MatrixCallAnswerEvent`: when a
            called user wishes to pick the call.
        * :class:`platypush.message.event.matrix.MatrixCallHangupEvent`: when a
            called user exits the call.
        * :class:`platypush.message.event.matrix.MatrixEncryptedMessageEvent`:
            when a message is received but the client doesn't have the E2E keys
            to decrypt it, or encryption has not been enabled.

    """

    def __init__(
        self,
        server_url: str = 'https://matrix.to',
        user_id: str | None = None,
        password: str | None = None,
        access_token: str | None = None,
        device_name: str | None = 'platypush',
        device_id: str | None = None,
        download_path: str | None = None,
        autojoin_on_invite: bool = True,
        autotrust_devices: bool = False,
        autotrust_devices_whitelist: Collection[str] | None = None,
        autotrust_users_whitelist: Collection[str] | None = None,
        autotrust_rooms_whitelist: Collection[str] | None = None,
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
        :param user_id: user_id, in the format ``@user:example.org``, or just
            the username if the account is hosted on the same server configured in
            the ``server_url``.
        :param password: User password.
        :param access_token: User access token.
        :param device_name: The name of this device/connection (default: ``platypush``).
        :param device_id: Use an existing ``device_id`` for the sessions.
        :param download_path: The folder where downloaded media will be saved
            (default: ``~/Downloads``).
        :param autojoin_on_invite: Whether the account should automatically
            join rooms upon invite. If false, then you may want to implement your
            own logic in an event hook when a
            :class:`platypush.message.event.matrix.MatrixRoomInviteEvent` event is
            received, and call the :meth:`.join` method if required.
        :param autotrust_devices: If set to True, the plugin will automatically
            trust the devices on encrypted rooms. Set this property to True
            only if you only plan to use a bot on trusted rooms. Note that if
            no automatic trust mechanism is set you may need to explicitly
            create your logic for trusting users - either with a hook when
            :class:`platypush.message.event.matrix.MatrixSyncEvent` is
            received, or when a room is joined, or before sending a message.
        :param autotrust_devices_whitelist: Automatically trust devices with IDs
            IDs provided in this list.
        :param autotrust_users_whitelist: Automatically trust devices from the
            user IDs provided in this list.
        :param autotrust_rooms_whitelist: Automatically trust devices on the
            room IDs provided in this list.
        """
        super().__init__(**kwargs)
        if not (server_url.startswith('http://') or server_url.startswith('https://')):
            server_url = f'https://{server_url}'
        self._server_url = server_url
        server_name = self._server_url.split('/')[2].split(':')[0]

        if user_id and not re.match(user_id, '^@[a-zA-Z0-9.-_]+:.+'):
            user_id = f'@{user_id}:{server_name}'

        self._user_id = user_id
        self._password = password
        self._access_token = access_token
        self._device_name = device_name
        self._device_id = device_id
        self._download_path = download_path or os.path.join(
            os.path.expanduser('~'), 'Downloads'
        )

        self._autojoin_on_invite = autojoin_on_invite
        self._autotrust_devices = autotrust_devices
        self._autotrust_devices_whitelist = set(autotrust_devices_whitelist or [])
        self._autotrust_users_whitelist = set(autotrust_users_whitelist or [])
        self._autotrust_rooms_whitelist = set(autotrust_rooms_whitelist or [])
        self._workdir = os.path.join(Config.get('workdir'), 'matrix')  # type: ignore
        self._credentials_file = os.path.join(self._workdir, 'credentials.json')
        self._processed_responses = {}
        self._client = self._get_client()
        pathlib.Path(self._workdir).mkdir(parents=True, exist_ok=True)

    def _get_client(self) -> MatrixClient:
        return MatrixClient(
            homeserver=self._server_url,
            user=self._user_id,
            credentials_file=self._credentials_file,
            autojoin_on_invite=self._autojoin_on_invite,
            autotrust_devices=self._autotrust_devices,
            autotrust_devices_whitelist=self._autotrust_devices_whitelist,
            autotrust_rooms_whitelist=self._autotrust_rooms_whitelist,
            autotrust_users_whitelist=self._autotrust_users_whitelist,
            device_id=self._device_id,
        )

    @property
    def client(self) -> MatrixClient:
        if not self._client:
            self._client = self._get_client()
        return self._client

    async def _login(self) -> MatrixClient:
        await self.client.login(
            password=self._password,
            device_name=self._device_name,
            token=self._access_token,
        )

        return self.client

    async def listen(self):
        while not self.should_stop():
            await self._login()

            try:
                await self.client.sync_forever(timeout=30000, full_state=True)
            except KeyboardInterrupt:
                pass
            except Exception as e:
                self.logger.exception(e)
            finally:
                try:
                    await self.client.close()
                finally:
                    self._client = None

    def _loop_execute(self, coro: Coroutine):
        assert self._loop, 'The loop is not running'

        try:
            ret = asyncio.run_coroutine_threadsafe(coro, self._loop).result()
        except OlmUnverifiedDeviceError as e:
            raise AssertionError(str(e))

        assert not isinstance(ret, ErrorResponse), ret.message
        if hasattr(ret, 'transport_response'):
            response = ret.transport_response
            assert response.ok, f'{coro} failed with status {response.status}'

        return ret

    def _process_local_attachment(self, attachment: str, room_id: str) -> dict:
        attachment = os.path.expanduser(attachment)
        assert os.path.isfile(attachment), f'{attachment} is not a valid file'

        filename = os.path.basename(attachment)
        mime_type = get_mime_type(attachment) or 'application/octet-stream'
        message_type = mime_type.split('/')[0]
        if message_type not in {'audio', 'video', 'image'}:
            message_type = 'text'

        encrypted = self.get_room(room_id).output.get('encrypted', False)  # type: ignore
        url = self.upload(
            attachment, name=filename, content_type=mime_type, encrypt=encrypted
        ).output  # type: ignore

        return {
            'url': url,
            'msgtype': 'm.' + message_type,
            'body': filename,
            'info': {
                'size': os.stat(attachment).st_size,
                'mimetype': mime_type,
            },
        }

    def _process_remote_attachment(self, attachment: str) -> dict:
        parsed_url = urlparse(attachment)
        server = parsed_url.netloc.strip('/')
        media_id = parsed_url.path.strip('/')

        response = self._loop_execute(self.client.download(server, media_id))

        content_type = response.content_type
        message_type = content_type.split('/')[0]
        if message_type not in {'audio', 'video', 'image'}:
            message_type = 'text'

        return {
            'url': attachment,
            'msgtype': 'm.' + message_type,
            'body': response.filename,
            'info': {
                'size': len(response.body),
                'mimetype': content_type,
            },
        }

    def _process_attachment(self, attachment: str, room_id: str):
        if attachment.startswith('mxc://'):
            return self._process_remote_attachment(attachment)
        return self._process_local_attachment(attachment, room_id=room_id)

    @action
    def send_message(
        self,
        room_id: str,
        message_type: str = 'text',
        body: str | None = None,
        attachment: str | None = None,
        tx_id: str | None = None,
        ignore_unverified_devices: bool = False,
    ):
        """
        Send a message to a room.

        :param room_id: Room ID.
        :param body: Message body.
        :param attachment: Path to a local file to send as an attachment, or
            URL of an existing Matrix media ID in the format
            ``mxc://<server>/<media_id>``. If the attachment is a local file,
            the file will be automatically uploaded, ``message_type`` will be
            automatically inferred from the file and the ``body`` will be
            replaced by the filename.
        :param message_type: Message type. Supported: `text`, `audio`, `video`,
            `image`. Default: `text`.
        :param tx_id: Unique transaction ID to associate to this message.
        :param ignore_unverified_devices: If true, unverified devices will be
            ignored. Otherwise, if the room is encrypted and it contains
            devices that haven't been marked as trusted, the message
            delivery may fail (default: False).
        :return: .. schema:: matrix.MatrixEventIdSchema
        """
        content = {
            'msgtype': 'm.' + message_type,
            'body': body,
        }

        if attachment:
            content.update(self._process_attachment(attachment, room_id=room_id))

        ret = self._loop_execute(
            self.client.room_send(
                message_type='m.room.message',
                room_id=room_id,
                tx_id=tx_id,
                ignore_unverified_devices=ignore_unverified_devices,
                content=content,
            )
        )

        ret = self._loop_execute(ret.transport_response.json())
        return MatrixEventIdSchema().dump(ret)

    @action
    def get_profile(self, user_id: str):
        """
        Retrieve the details about a user.

        :param user_id: User ID.
        :return: .. schema:: matrix.MatrixProfileSchema
        """
        profile = self._loop_execute(self.client.get_profile(user_id))  # type: ignore
        profile.user_id = user_id
        return MatrixProfileSchema().dump(profile)

    @action
    def get_room(self, room_id: str):
        """
        Retrieve the details about a room.

        :param room_id: room ID.
        :return: .. schema:: matrix.MatrixRoomSchema
        """
        response = self._loop_execute(self.client.room_get_state(room_id))  # type: ignore
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
    def get_my_devices(self):
        """
        Get the list of devices associated to the current user.

        :return: .. schema:: matrix.MatrixMyDeviceSchema(many=True)
        """
        response = self._loop_execute(self.client.devices())
        return MatrixMyDeviceSchema().dump(response.devices, many=True)

    @action
    def get_device(self, device_id: str):
        """
        Get the info about a device given its ID.

        :return: .. schema:: matrix.MatrixDeviceSchema
        """
        return MatrixDeviceSchema().dump(self._get_device(device_id))

    @action
    def get_joined_rooms(self):
        """
        Retrieve the rooms that the user has joined.
        """
        response = self._loop_execute(self.client.joined_rooms())
        return [self.get_room(room_id).output for room_id in response.rooms]  # type: ignore

    @action
    def upload_keys(self):
        """
        Synchronize the E2EE keys with the homeserver.
        """
        self._loop_execute(self.client.keys_upload())

    def _get_device(self, device_id: str) -> OlmDevice:
        device = self.client.get_device(device_id)
        assert device, f'No such device_id: {device_id}'
        return device

    @action
    def trust_device(self, device_id: str):
        """
        Mark a device as trusted.

        :param device_id: Device ID.
        """
        device = self._get_device(device_id)
        self.client.verify_device(device)

    @action
    def untrust_device(self, device_id: str):
        """
        Mark a device as untrusted.

        :param device_id: Device ID.
        """
        device = self._get_device(device_id)
        self.client.unverify_device(device)

    @action
    def mxc_to_http(self, url: str, homeserver: str | None = None) -> str:
        """
        Convert a Matrix URL (in the format ``mxc://server/media_id``) to an
        HTTP URL.

        Note that invoking this function on a URL containing encrypted content
        (i.e. a URL containing media sent to an encrypted room) will provide a
        URL that points to encrypted content. The best way to deal with
        encrypted media is by using :meth:`.download` to download the media
        locally.

        :param url: The MXC URL to be converted.
        :param homeserver: The hosting homeserver (default: the same as the URL).
        :return: The converted HTTP(s) URL.
        """
        http_url = Api.mxc_to_http(url, homeserver=homeserver)
        assert http_url, f'Could not convert URL {url}'
        return http_url

    @action
    def download(
        self,
        url: str,
        download_path: str | None = None,
        filename: str | None = None,
        allow_remote=True,
    ):
        """
        Download a file given its Matrix URL.

        Note that URLs that point to encrypted resources will be automatically
        decrypted only if they were received on a room joined by this account.

        :param url: Matrix URL, in the format ``mxc://<server>/<media_id>``.
        :param download_path: Override the default ``download_path`` (output
            directory for the downloaded file).
        :param filename: Name of the output file (default: inferred from the
            remote resource).
        :param allow_remote: Indicates to the server that it should not attempt
            to fetch the media if it is deemed remote. This is to prevent
            routing loops where the server contacts itself.
        :return: .. schema:: matrix.MatrixDownloadedFileSchema
        """
        parsed_url = urlparse(url)
        server = parsed_url.netloc.strip('/')
        media_id = parsed_url.path.strip('/')

        response = self._loop_execute(
            self.client.download(
                server, media_id, filename=filename, allow_remote=allow_remote
            )
        )

        if not download_path:
            download_path = self._download_path
        if not filename:
            filename = response.filename or media_id

        outfile = os.path.join(str(download_path), str(filename))
        pathlib.Path(download_path).mkdir(parents=True, exist_ok=True)

        with open(outfile, 'wb') as f:
            f.write(response.body)

        return MatrixDownloadedFileSchema().dump(
            {
                'url': url,
                'path': outfile,
                'size': len(response.body),
                'content_type': response.content_type,
            }
        )

    @action
    def upload(
        self,
        file: str,
        name: str | None = None,
        content_type: str | None = None,
        encrypt: bool = False,
    ) -> str:
        """
        Upload a file to the server.

        :param file: Path to the file to upload.
        :param name: Filename to be used for the remote file (default: same as
            the local file).
        :param content_type: Specify a content type for the file (default:
            inferred from the file's extension and content).
        :param encrypt: Encrypt the file (default: False).
        :return: The Matrix URL of the uploaded resource.
        """
        rs = self._loop_execute(
            self.client.upload_file(file, name, content_type, encrypt)
        )

        return rs[0].content_uri

    @action
    def invite_to_room(self, room_id: str, user_id: str):
        """
        Invite a user to a room.

        :param room_id: Room ID.
        :param user_id: User ID.
        """
        self._loop_execute(self.client.room_invite(room_id, user_id))

    @action
    def join_room(self, room_id: str):
        """
        Join a room.

        :param room_id: Room ID.
        """
        self._loop_execute(self.client.join(room_id))

    @action
    def leave_room(self, room_id: str):
        """
        Leave a joined room.

        :param room_id: Room ID.
        """
        self._loop_execute(self.client.room_leave(room_id))


# vim:sw=4:ts=4:et:
