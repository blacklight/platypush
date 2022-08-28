import asyncio
import datetime
import json
import logging
import os
import pathlib
import threading

from dataclasses import dataclass
from typing import Collection, Dict, Optional, Union
from urllib.parse import urlparse

from async_lru import alru_cache
from nio import (
    AsyncClient,
    AsyncClientConfig,
    CallAnswerEvent,
    CallHangupEvent,
    CallInviteEvent,
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
    SyncResponse,
    ToDeviceError,
    UnknownEncryptedEvent,
    UnknownEvent,
)

import aiofiles
import aiofiles.os

from nio.client.async_client import client_session
from nio.client.base_client import logged_in
from nio.crypto import decrypt_attachment
from nio.crypto.device import OlmDevice
from nio.events.ephemeral import ReceiptEvent, TypingNoticeEvent
from nio.events.presence import PresenceEvent
from nio.responses import DownloadResponse, RoomMessagesResponse

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
    MatrixRoomSeenReceiptEvent,
    MatrixRoomTopicChangedEvent,
    MatrixRoomTypingStartEvent,
    MatrixRoomTypingStopEvent,
    MatrixSyncEvent,
    MatrixUserPresenceEvent,
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
        config: Optional[AsyncClientConfig] = None,
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
        self._last_batches_by_room = {}
        self._typing_users_by_room = {}

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

    @logged_in
    async def sync(self, *args, **kwargs) -> SyncResponse:
        response = await super().sync(*args, **kwargs)
        assert isinstance(response, SyncResponse), str(response)
        self._last_batches_by_room.update(
            {
                room_id: {
                    'prev_batch': room.timeline.prev_batch,
                    'next_batch': response.next_batch,
                }
                for room_id, room in response.rooms.join.items()
            }
        )

        return response

    @logged_in
    async def room_messages(
        self, room_id: str, start: str | None = None, *args, **kwargs
    ) -> RoomMessagesResponse:
        if not start:
            start = self._last_batches_by_room.get(room_id, {}).get('prev_batch')
            assert start, (
                f'No sync batches were found for room {room_id} and no start'
                'batch has been provided'
            )

        response = await super().room_messages(room_id, start, *args, **kwargs)
        assert isinstance(response, RoomMessagesResponse), str(response)
        return response

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

    def get_device(self, device_id: str) -> Optional[OlmDevice]:
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
        self.add_ephemeral_callback(self._on_typing, TypingNoticeEvent)  # type: ignore
        self.add_ephemeral_callback(self._on_receipt, ReceiptEvent)  # type: ignore
        self.add_presence_callback(self._on_presence, PresenceEvent)  # type: ignore

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

    @client_session
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
        self, room: Optional[MatrixRoom], event: Optional[Event] = None
    ) -> dict:
        sender_id = getattr(event, 'sender', None)
        sender = (
            await self.get_profile(sender_id) if sender_id else None  # type: ignore
        )

        return {
            'server_url': self.homeserver,
            'sender_id': sender_id,
            'sender_display_name': sender.displayname if sender else None,
            'sender_avatar_url': sender.avatar_url if sender else None,
            **(
                {
                    'room_id': room.room_id,
                    'room_name': room.name,
                    'room_topic': room.topic,
                }
                if room
                else {}
            ),
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
        event: Union[
            RoomMessageText, RoomMessageMedia, RoomEncryptedMedia, StickerEvent
        ],
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

    async def _on_typing(self, room: MatrixRoom, event: TypingNoticeEvent):
        users = set(event.users)
        typing_users = self._typing_users_by_room.get(room.room_id, set())
        start_typing_users = users.difference(typing_users)
        stop_typing_users = typing_users.difference(users)

        for user in start_typing_users:
            event.sender = user  # type: ignore
            get_bus().post(
                MatrixRoomTypingStartEvent(
                    **(await self._event_base_args(room, event)),  # type: ignore
                    sender=user,
                )
            )

        for user in stop_typing_users:
            event.sender = user  # type: ignore
            get_bus().post(
                MatrixRoomTypingStopEvent(
                    **(await self._event_base_args(room, event)),  # type: ignore
                )
            )

        self._typing_users_by_room[room.room_id] = users

    async def _on_receipt(self, room: MatrixRoom, event: ReceiptEvent):
        if self._first_sync_performed.is_set():
            for receipt in event.receipts:
                event.sender = receipt.user_id  # type: ignore
                get_bus().post(
                    MatrixRoomSeenReceiptEvent(
                        **(await self._event_base_args(room, event)),  # type: ignore
                    )
                )

    async def _on_presence(self, event: PresenceEvent):
        if self._first_sync_performed.is_set():
            last_active = (
                (
                    datetime.datetime.now()
                    - datetime.timedelta(seconds=event.last_active_ago / 1000)
                )
                if event.last_active_ago
                else None
            )

            event.sender = event.user_id  # type: ignore
            get_bus().post(
                MatrixUserPresenceEvent(
                    **(await self._event_base_args(None, event)),  # type: ignore
                    is_active=event.currently_active or False,
                    last_active=last_active,
                )
            )

    async def _on_unknown_encrypted_event(
        self, room: MatrixRoom, event: Union[UnknownEncryptedEvent, MegolmEvent]
    ):
        if self._first_sync_performed.is_set():
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
        name: Optional[str] = None,
        content_type: Optional[str] = None,
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


# vim:sw=4:ts=4:et:
