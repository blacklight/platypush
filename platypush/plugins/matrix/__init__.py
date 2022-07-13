import datetime
import json
import multiprocessing
import os
import pathlib
import requests
from abc import ABC, abstractmethod
from urllib.parse import urljoin
from typing import Optional, Collection, Dict, Tuple, Any

from platypush.config import Config
from platypush.context import get_bus
from platypush.message.event.matrix import (
    MatrixEvent,
    MatrixRoomTopicChangeEvent,
    MatrixMessageEvent,
    MatrixRoomJoinEvent,
    MatrixRoomLeaveEvent,
    MatrixRoomInviteEvent,
    MatrixRoomInviteMeEvent,
)

from platypush.plugins import RunnablePlugin, action


class RetrieveWorker(ABC):
    def __init__(self, server_url: str, access_token: str):
        self._server_url = server_url
        self._access_token = access_token

    @abstractmethod
    def _url(self, id: int | str) -> str:
        raise NotImplementedError()

    @abstractmethod
    def _process_response(self, rs: dict) -> dict:
        raise NotImplementedError()

    def __call__(self, id: str) -> Tuple[str, dict]:
        url = urljoin(self._server_url, self._url(id))
        rs = requests.get(
            url,
            headers={
                'Authorization': f'Bearer {self._access_token}',
            },
        )

        rs.raise_for_status()
        return (id, self._process_response(rs.json()))


class UserRetrieveWorker(RetrieveWorker):
    def _url(self, id: str) -> str:
        return f'/_matrix/client/r0/profile/{id}'

    def _process_response(self, rs: dict) -> dict:
        return {
            'display_name': rs.get('displayname'),
            'avatar_url': rs.get('avatar_url'),
        }


class RoomRetrieveWorker:
    def _url(self, id: str) -> str:
        return f'/_matrix/client/r0/room/{id}'

    def _process_response(self, rs: dict) -> dict:
        return {
            'display_name': rs.get('displayname'),
            'avatar_url': rs.get('avatar_url'),
        }


class MatrixPlugin(RunnablePlugin):
    """
    Matrix chat integration.

    Triggers:

        * :class:`platypush.message.event.matrix.MatrixMessageEvent`: when a message is received.
        * :class:`platypush.message.event.matrix.MatrixRoomJoinEvent`: when a user joins a room.
        * :class:`platypush.message.event.matrix.MatrixRoomLeaveEvent`: when a user leaves a room.
        * :class:`platypush.message.event.matrix.MatrixRoomInviteEvent`: when a user (other than the
            currently logged one) is invited to a room.
        * :class:`platypush.message.event.matrix.MatrixRoomMeInviteEvent`: when the currently logged in
            user is invited to a room.
        * :class:`platypush.message.event.matrix.MatrixRoomTopicChangeEvent`: when the topic/title of a room changes.

    """

    def __init__(
        self,
        server_url: str = 'https://matrix.to',
        username: str | None = None,
        password: str | None = None,
        access_token: str | None = None,
        autojoin_on_invite: bool = False,
        **kwargs,
    ):
        """
        Authentication requires either username/password or an access token.

        If you don't want to provide cleartext credentials in the configuration, you can
        retrieve an access token offline through the following request::

            curl -XPOST '{"type":"m.login.password", "user":"username", "password":"password"}' \
                "https://matrix.example.com/_matrix/client/r0/login"

        This may be required if the user or the instance enforce 2FA.

        :param server_url: Default Matrix instance base URL (default: ``https://matrix.to``).
        :param username: Default username. Provide either username/password _or_ an access token.
        :param password: Default password. Provide either username/password _or_ an access token.
        :param access_token: Default access token. Provide either username/password _or_ an access token.
        :param autojoin_on_invite: Whether the account should automatically join rooms
            upon invite. If false (default value), then you may want to implement your own
            logic in an event hook when a :class:`platypush.message.event.matrix.MatrixRoomInviteMeEvent`
            event is received, and call the :meth:`.join` method if required.
        """
        super().__init__(**kwargs)
        self._server_url = server_url
        self._user_id = None
        self._autojoin_on_invite = autojoin_on_invite
        self._workdir = os.path.join(Config.get('workdir'), 'matrix')  # type: ignore
        pathlib.Path(self._workdir).mkdir(parents=True, exist_ok=True)

        self._sessions_file = os.path.join(self._workdir, 'sessions.json')
        self._credentials_file = os.path.join(self._workdir, 'credentials.json')
        self._users_cache_file = os.path.join(self._workdir, 'users.json')
        self._rooms_cache_file = os.path.join(self._workdir, 'rooms.json')
        self._users_cache = {}
        self._rooms_cache = {}
        self._set_credentials(username, password, access_token, overwrite=True)

    def _set_credentials(
        self,
        username: str | None = None,
        password: str | None = None,
        access_token: str | None = None,
        overwrite: bool = False,
    ):
        if username or overwrite:
            self._username = username
        if password or overwrite:
            self._password = password
        if access_token or overwrite:
            self._access_token = access_token

    def _execute(self, url: str, method: str = 'get', **kwargs):
        if self._access_token:
            kwargs['headers'] = {
                'Authorization': f'Bearer {self._access_token}',
                **kwargs.get('headers', {}),
            }

        url = urljoin(self._server_url, f'/_matrix/client/{url.lstrip("/")}')
        req_method = getattr(requests, method.lower())
        rs = req_method(url, **kwargs)
        rs.raise_for_status()
        rs = rs.json()
        assert not rs.get('error'), rs.get('error')
        return rs

    def _save_credentials(self, credentials: dict):
        with open(self._credentials_file, 'w') as f:
            json.dump(credentials, f)

    def _refresh_user_id(self):
        devices = self._execute('/v3/devices').get('devices', [])
        assert devices, 'The user is not logged into any devices'
        self._user_id = devices[0]['user_id']

    @action
    def login(
        self,
        server_url: str | None = None,
        username: str | None = None,
        password: str | None = None,
        access_token: str | None = None,
    ):
        """
        Login to an instance if username/password/access_token were not specified in the plugin
        configuration. Otherwise, change the currently logged user or instance.

        :param server_url: New Matrix instance base URL.
        :param username: New username.
        :param password: New user password.
        :param access_token: New access token.
        """
        self._server_url = server_url or self._server_url
        self._set_credentials(username, password, access_token, overwrite=False)

        if self._access_token:
            self._refresh_user_id()
        elif self._username and self._password:
            rs = self._execute(
                '/r0/login',
                method='post',
                json={
                    'type': 'm.login.password',
                    'user': self._username,
                    'password': self._password,
                    'initial_device_display_name': 'Platypush Matrix integration',
                },
            )

            assert rs.get('access_token'), 'No access token provided by the server'
            self._access_token = rs['access_token']
            self._user_id = rs['user_id']
            self._save_credentials(rs)
        elif os.path.isfile(self._credentials_file):
            with open(self._credentials_file, 'r') as f:
                self._access_token = json.load(f)['access_token']
            self._refresh_user_id()
        else:
            raise AssertionError(
                'No username, password and access token provided nor stored'
            )

        self.logger.info(
            f'Successfully logged in to {self._server_url} as {self._user_id}'
        )

    @staticmethod
    def _timestamp_to_datetime(t: int | float) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(t / 1000)

    def _parse_event(
        self, room_id: str, event: dict, users: dict
    ) -> Optional[MatrixEvent]:
        evt_type = event.get('type')
        evt_class = None
        args: Dict[str, Any] = {
            'server_url': self._server_url,
            'room_id': room_id,
        }

        if event.get('sender') and isinstance(event.get('sender'), str):
            cached_user = users.get(event['sender'], {})
            args['sender_id'] = event['sender']
            args['sender_display_name'] = cached_user.get('display_name')
            args['sender_avatar_url'] = cached_user.get('avatar_url')

        if event.get('origin_server_ts'):
            args['server_timestamp'] = self._timestamp_to_datetime(
                event['origin_server_ts']
            )

        if evt_type == 'm.room.topic':
            evt_class = MatrixRoomTopicChangeEvent
            args['topic'] = event.get('content', {}).get('topic')  # type: ignore
        elif evt_type == 'm.room.message':
            evt_class = MatrixMessageEvent
            args['body'] = event.get('content', {}).get('body')  # type: ignore
        elif evt_type == 'm.room.member':
            membership = event.get('content', {}).get('membership')
            if membership == 'join':
                evt_class = MatrixRoomJoinEvent
            elif membership == 'invite':
                evt_class = MatrixRoomInviteEvent
            elif membership == 'leave':
                evt_class = MatrixRoomLeaveEvent

        if evt_class:
            return evt_class(**args)

    def _parse_invite_event(
        self, room_id: str, events: Collection[dict]
    ) -> MatrixRoomInviteMeEvent:
        evt_args: Dict[str, Any] = {
            'server_url': self._server_url,
            'room_id': room_id,
        }

        for event in events:
            evt_type = event.get('type')
            if evt_type == 'm.room.name':
                evt_args['room_name'] = event.get('content', {}).get('name')
            elif evt_type == 'm.room.topic':
                evt_args['room_topic'] = event.get('content', {}).get('topic')
            if event.get('origin_server_ts'):
                evt_args['server_timestamp'] = self._timestamp_to_datetime(
                    event['origin_server_ts']
                )

        if evt_args.get('room_name'):
            self._rooms_cache[room_id] = {
                'room_id': room_id,
                'room_name': evt_args['room_name'],
                'room_topic': evt_args.get('room_topic'),
            }

            self._rewrite_rooms_cache()

        return MatrixRoomInviteMeEvent(**evt_args)

    def _retrieve_users_info(self, users: Collection[str]) -> Dict[str, dict]:
        users_info = {user: {} for user in users}
        retrieve = UserRetrieveWorker(self._server_url, self._access_token or '')
        with multiprocessing.Pool(4) as pool:
            pool_res = pool.map(retrieve, users_info.keys())

        return {
            user_id: {
                'user_id': user_id,
                **info,
            }
            for user_id, info in pool_res
        }

    def _extract_senders(self, rooms) -> Dict[str, dict]:
        cache_has_changes = False
        senders = set()

        for room in rooms:
            room_events = room.get('timeline', {}).get('events', [])
            for evt in room_events:
                if evt.get('type') == 'm.room.member':
                    cache_has_changes = True
                    self._users_cache[evt['sender']] = {
                        'user_id': evt['sender'],
                        'display_name': evt.get('content', {}).get('displayname'),
                        'avatar_url': evt.get('content', {}).get('avatar_url'),
                    }

            senders.update({evt['sender'] for evt in room_events if evt.get('sender')})

        missing_senders = {user for user in senders if user not in self._users_cache}

        if missing_senders:
            cache_has_changes = True
            self._users_cache.update(self._retrieve_users_info(missing_senders))

        senders_map = {
            user: self._users_cache.get(user, {'user_id': user}) for user in senders
        }

        if cache_has_changes:
            self._rewrite_users_cache()

        return senders_map

    def _process_events(self, events: dict) -> Collection[MatrixEvent]:
        rooms = events.get('rooms', {})
        joined_rooms = rooms.get('join', {})
        invited_rooms = rooms.get('invite', {})
        parsed_events = []
        senders = self._extract_senders(joined_rooms.values())

        # Create events
        for room_id, room in joined_rooms.items():
            room_events = room.get('timeline', {}).get('events', [])
            parsed_room_events = [
                self._parse_event(room_id=room_id, event=event, users=senders)
                for event in room_events
            ]

            parsed_events.extend([evt for evt in parsed_room_events if evt])

        for room_id, room in invited_rooms.items():
            room_events = room.get('invite_state', {}).get('events', [])
            parsed_room_event = self._parse_invite_event(
                room_id=room_id, events=room_events
            )
            parsed_events.append(parsed_room_event)

            if self._autojoin_on_invite:
                self.join(room_id)

        parsed_events.sort(key=lambda e: e.server_timestamp)
        return parsed_events

    def _reload_users_cache(self):
        if os.path.isfile(self._users_cache_file):
            with open(self._users_cache_file, 'r') as f:
                self._users_cache.update(json.load(f))

    def _rewrite_users_cache(self):
        with open(self._users_cache_file, 'w') as f:
            json.dump(self._users_cache, f)

    def _reload_rooms_cache(self):
        if os.path.isfile(self._rooms_cache_file):
            with open(self._rooms_cache_file, 'r') as f:
                self._rooms_cache.update(json.load(f))

    def _rewrite_rooms_cache(self):
        with open(self._rooms_cache_file, 'w') as f:
            json.dump(self._rooms_cache, f)

    @action
    def sync(self):
        """
        Sync the state for the currently logged session.
        """
        next_batch = None
        sessions = {}
        if os.path.isfile(self._sessions_file):
            with open(self._sessions_file, 'r') as f:
                sessions = json.load(f)
            next_batch = sessions.get(self._user_id, {}).get('next_batch')

        if not next_batch:
            self.logger.info('Synchronizing Matrix events')

        rs = self._execute('/r0/sync', params={'since': next_batch})
        events = self._process_events(rs)
        if events and next_batch:
            for event in events:
                get_bus().post(event)

        if not sessions.get(self._user_id):
            sessions[self._user_id] = {}

        sessions[self._user_id]['next_batch'] = rs.get('next_batch')
        with open(self._sessions_file, 'w') as f:
            json.dump(sessions, f)

        if not next_batch:
            self.logger.info('Matrix events synchronized')

    @action
    def join(self, room_id: str):
        """
        Join a room by ID.

        :param room_id: Room ID or alias.
        """
        self._execute(f'/v3/join/{room_id}', method='post')
        self.logger.info('Successfully joined room %s', room_id)

    def main(self):
        self.login()
        self._reload_users_cache()
        self._reload_rooms_cache()

        while not self._should_stop.is_set():
            try:
                self.sync()
            finally:
                self._should_stop.wait(timeout=10)


# vim:sw=4:ts=4:et:
