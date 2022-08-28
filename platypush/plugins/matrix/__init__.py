import asyncio
import logging
import os
import pathlib
import re

from dataclasses import dataclass
from typing import Collection, Coroutine, Sequence
from urllib.parse import urlparse

from nio import (
    Api,
    ErrorResponse,
    MatrixRoom,
    RoomMessage,
)

from nio.api import MessageDirection, RoomVisibility

from nio.crypto.device import OlmDevice
from nio.exceptions import OlmUnverifiedDeviceError

from platypush.config import Config

from platypush.plugins import AsyncRunnablePlugin, action
from platypush.schemas.matrix import (
    MatrixDeviceSchema,
    MatrixDownloadedFileSchema,
    MatrixEventIdSchema,
    MatrixMemberSchema,
    MatrixMessagesResponseSchema,
    MatrixMyDeviceSchema,
    MatrixProfileSchema,
    MatrixRoomIdSchema,
    MatrixRoomSchema,
)

from platypush.utils import get_mime_type

from .client import MatrixClient

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
        - Select "*Verify through emoji*". A list of emojis should be prompted.
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
        * :class:`platypush.message.event.matrix.MatrixRoomTypingStartEvent`:
            when a user in a room starts typing.
        * :class:`platypush.message.event.matrix.MatrixRoomTypingStopEvent`:
            when a user in a room stops typing.
        * :class:`platypush.message.event.matrix.MatrixRoomSeenReceiptEvent`:
            when the last message seen by a user in a room is updated.
        * :class:`platypush.message.event.matrix.MatrixUserPresenceEvent`:
            when a user comes online or goes offline.

    """

    def __init__(
        self,
        server_url: str = 'https://matrix-client.matrix.org',
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

        :param server_url: Default Matrix instance base URL (default:
            ``https://matrix-client.matrix.org``).
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
                self.logger.info('Waiting 10 seconds before reconnecting')
                await asyncio.sleep(10)
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
                room_args['encrypted'] = True
            elif evt.get('type') == 'm.room.name':
                room_params['name'] = evt.get('content', {}).get('name')
            elif evt.get('type') == 'm.room.topic':
                room_params['topic'] = evt.get('content', {}).get('topic')

        room = MatrixRoom(**room_args)
        for k, v in room_params.items():
            setattr(room, k, v)
        return MatrixRoomSchema().dump(room)

    @action
    def get_messages(
        self,
        room_id: str,
        start: str | None = None,
        end: str | None = None,
        backwards: bool = True,
        limit: int = 10,
    ):
        """
        Retrieve a list of messages from a room.

        :param room_id: Room ID.
        :param start: Start retrieving messages from this batch ID (default:
            latest batch returned from a call to ``sync``).
        :param end: Retrieving messages until this batch ID.
        :param backwards: Set to True if you want to retrieve messages starting
            from the most recent, in descending order (default). Otherwise, the
            first returned message will be the oldest and messages will be
            returned in ascending order.
        :param limit: Maximum number of messages to be returned (default: 10).
        :return: .. schema:: matrix.MatrixMessagesResponseSchema
        """
        response = self._loop_execute(
            self.client.room_messages(
                room_id,
                start=start,
                end=end,
                limit=limit,
                direction=(
                    MessageDirection.back if backwards else MessageDirection.front
                ),
            )
        )

        response.chunk = [m for m in response.chunk if isinstance(m, RoomMessage)]
        return MatrixMessagesResponseSchema().dump(response)

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
    def update_device(self, device_id: str, display_name: str | None = None):
        """
        Update information about a user's device.

        :param display_name: New display name.
        :return: .. schema:: matrix.MatrixDeviceSchema
        """
        content = {}
        if display_name:
            content['display_name'] = display_name

        self._loop_execute(self.client.update_device(device_id, content))
        return MatrixDeviceSchema().dump(self._get_device(device_id))

    @action
    def delete_devices(
        self,
        devices: Sequence[str],
        username: str | None = None,
        password: str | None = None,
    ):
        """
        Delete a list of devices from the user's authorized list and invalidate
        their access tokens.

        :param devices: List of devices that should be deleted.
        :param username: Username, if the server requires authentication upon
            device deletion.
        :param password: User password, if the server requires authentication
            upon device deletion.
        """
        auth = {}
        if username and password:
            auth = {'type': 'm.login.password', 'user': username, 'password': password}

        self._loop_execute(self.client.delete_devices([*devices], auth=auth))

    @action
    def get_joined_rooms(self):
        """
        Retrieve the rooms that the user has joined.

        :return: .. schema:: matrix.MatrixRoomSchema(many=True)
        """
        response = self._loop_execute(self.client.joined_rooms())
        return [self.get_room(room_id).output for room_id in response.rooms]  # type: ignore

    @action
    def get_room_members(self, room_id: str):
        """
        Retrieve the list of users joined into a room.

        :param room_id: The room ID.
        :return: .. schema:: matrix.MatrixMemberSchema(many=True)
        """
        response = self._loop_execute(self.client.joined_members(room_id))
        return MatrixMemberSchema().dump(response.members, many=True)

    @action
    def room_alias_to_id(self, alias: str) -> str:
        """
        Convert a room alias (in the format ``#alias:matrix.example.org``) to a
        room ID (in the format ``!aBcDeFgHiJkMnO:matrix.example.org``).

        :param alias: The room alias.
        :return: The room ID, as a string.
        """
        response = self._loop_execute(self.client.room_resolve_alias(alias))
        return response.room_id

    @action
    def add_room_alias(self, room_id: str, alias: str):
        """
        Add an alias to a room.

        :param room_id: An existing room ID.
        :param alias: The room alias.
        """
        self._loop_execute(self.client.room_put_alias(alias, room_id))

    @action
    def delete_room_alias(self, alias: str):
        """
        Delete a room alias.

        :param alias: The room alias.
        """
        self._loop_execute(self.client.room_delete_alias(alias))

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
    def create_room(
        self,
        name: str | None = None,
        alias: str | None = None,
        topic: str | None = None,
        is_public: bool = False,
        is_direct: bool = False,
        federate: bool = True,
        encrypted: bool = False,
        invite_users: Sequence[str] = (),
    ):
        """
        Create a new room on the server.

        :param name: Room name.
        :param alias: Custom alias for the canonical name. For example, if set
            to ``foo``, the alias for this room will be
            ``#foo:matrix.example.org``.
        :param topic: Room topic.
        :param is_public: Set to True if you want the room to be public and
            discoverable (default: False).
        :param is_direct: Set to True if this should be considered a direct
            room with only one user (default: False).
        :param federate: Whether you want to allow users from other servers to
            join the room (default: True).
        :param encrypted: Whether the room should be encrypted (default: False).
        :param invite_users: A list of user IDs to invite to the room.
        :return: .. schema:: matrix.MatrixRoomIdSchema
        """
        rs = self._loop_execute(
            self.client.room_create(
                name=name,
                alias=alias,
                topic=topic,
                is_direct=is_direct,
                federate=federate,
                invite=invite_users,
                visibility=(
                    RoomVisibility.public if is_public else RoomVisibility.private
                ),
                initial_state=[
                    {
                        'type': 'm.room.encryption',
                        'content': {
                            'algorithm': 'm.megolm.v1.aes-sha2',
                        },
                    }
                ]
                if encrypted
                else (),
            )
        )

        return MatrixRoomIdSchema().dump(rs)

    @action
    def invite(self, room_id: str, user_id: str):
        """
        Invite a user to a room.

        :param room_id: Room ID.
        :param user_id: User ID.
        """
        self._loop_execute(self.client.room_invite(room_id, user_id))

    @action
    def kick(self, room_id: str, user_id: str, reason: str | None = None):
        """
        Kick a user out of a room.

        :param room_id: Room ID.
        :param user_id: User ID.
        :param reason: Optional reason.
        """
        self._loop_execute(self.client.room_kick(room_id, user_id, reason))

    @action
    def ban(self, room_id: str, user_id: str, reason: str | None = None):
        """
        Ban a user from a room.

        :param room_id: Room ID.
        :param user_id: User ID.
        :param reason: Optional reason.
        """
        self._loop_execute(self.client.room_ban(room_id, user_id, reason))

    @action
    def unban(self, room_id: str, user_id: str):
        """
        Remove a user ban from a room.

        :param room_id: Room ID.
        :param user_id: User ID.
        """
        self._loop_execute(self.client.room_unban(room_id, user_id))

    @action
    def join(self, room_id: str):
        """
        Join a room.

        :param room_id: Room ID.
        """
        self._loop_execute(self.client.join(room_id))

    @action
    def leave(self, room_id: str):
        """
        Leave a joined room.

        :param room_id: Room ID.
        """
        self._loop_execute(self.client.room_leave(room_id))

    @action
    def forget(self, room_id: str):
        """
        Leave a joined room and forget its data as well as all the messages.

        If all the users leave a room, that room will be marked for deletion by
        the homeserver.

        :param room_id: Room ID.
        """
        self._loop_execute(self.client.room_forget(room_id))

    @action
    def set_display_name(self, display_name: str):
        """
        Set/change the display name for the current user.

        :param display_name: New display name.
        """
        self._loop_execute(self.client.set_displayname(display_name))

    @action
    def set_avatar(self, url: str):
        """
        Set/change the avatar URL for the current user.

        :param url: New avatar URL. It must be a valid ``mxc://`` link.
        """
        self._loop_execute(self.client.set_avatar(url))


# vim:sw=4:ts=4:et:
