import os
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from typing import Optional, List, Union, Dict

from platypush.context import Variable
from platypush.message.event.nextcloud import NextCloudActivityEvent
from platypush.plugins import RunnablePlugin, action


@dataclass
class ClientConfig:
    """
    Configuration for the NextCloud client.
    """

    url: str
    username: str
    password: str

    def to_dict(self):
        return {
            'url': self.url,
            'username': self.username,
            'password': self.password,
        }


class ShareType(IntEnum):
    """
    Enumerates the types of shares that can be created.
    """

    USER = 0
    GROUP = 1
    PUBLIC_LINK = 3
    EMAIL = 4
    FEDERATED_CLOUD_SHARE = 6
    CIRCLE = 7
    TALK_CONVERSATION = 10


class Permission(IntEnum):
    """
    Enumerates the permissions that can be granted to a user/group on a
    resource.
    """

    READ = 1
    UPDATE = 2
    CREATE = 4
    DELETE = 8
    SHARE = 16
    ALL = 31


_LAST_ACTIVITY_VARNAME = '_NEXTCLOUD_LAST_ACTIVITY_ID'


class NextcloudPlugin(RunnablePlugin):
    """
    Plugin to interact with a NextCloud instance.
    """

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        poll_interval: Optional[float] = 30.0,
        **kwargs,
    ):
        """
        :param url: URL to the index of your default NextCloud instance.
        :param username: Default NextCloud username.
        :param password: Default NextCloud password. If the user has 2FA
            enabled then you can generate an app password from the personal
            settings page of your NextCloud instance.
        :param poll_interval: How often the plugin should poll for new activity
            events (default: 30 seconds).
        """
        super().__init__(poll_interval=poll_interval, **kwargs)
        self.conf = ClientConfig(url=url, username=username, password=password)
        self._client = self._get_client(**self.conf.to_dict(), raise_on_empty=False)
        self._last_seen_id = None

    def _get_client(
        self,
        url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        raise_on_empty: bool = False,
    ):
        from nextcloud import NextCloud

        if not url:
            if not self.conf.url:
                if raise_on_empty:
                    raise AssertionError('No url/username/password provided')
                return None

            return NextCloud(
                endpoint=self.conf.url,
                user=self.conf.username,
                password=self.conf.password,
            )

        return NextCloud(endpoint=url, user=username, password=password)

    @property
    def _last_seen_var(self) -> Variable:
        return Variable(_LAST_ACTIVITY_VARNAME)

    @property
    def last_seen_id(self) -> int:
        if self._last_seen_id is None:
            self._last_seen_id = self._last_seen_var.get() or 0

        return int(self._last_seen_id)

    @last_seen_id.setter
    def last_seen_id(self, value: int = 0):
        self._last_seen_var.set(value)
        self._last_seen_id = value

    @staticmethod
    def _activity_to_event(activity: dict) -> NextCloudActivityEvent:
        activity_type = activity.pop('type')
        dt = datetime.fromisoformat(activity.pop('datetime'))
        return NextCloudActivityEvent(
            activity_type=activity_type, datetime=dt, **activity
        )

    @staticmethod
    def _get_permissions(permissions: Optional[List[str]]) -> int:
        int_perm = 0

        for perm in permissions or []:
            perm = perm.upper()
            assert hasattr(Permission, perm), (
                f'Unknown permissions type: {perm}. Supported permissions: '
                f'{[p.name.lower() for p in Permission]}'
            )

            if perm == 'ALL':
                int_perm = Permission.ALL.value
                break

            int_perm += getattr(Permission, perm).value

        return int_perm

    @staticmethod
    def _get_share_type(share_type: str) -> int:
        share_type = share_type.upper()
        assert hasattr(ShareType, share_type), (
            f'Unknown share type: {share_type}. Supported share types: '
            f'{[s.name.lower() for s in ShareType]}'
        )

        return getattr(ShareType, share_type).value

    def _execute(self, server_args: dict, method: str, *args, **kwargs):
        client = self._get_client(**server_args)
        func = getattr(client, method, None)
        assert func, f'No such NextCloud method: {method}'

        response = func(*args, **kwargs)
        assert response is not None, 'No response from NextCloud server'
        assert response.is_ok, (
            'Error on '
            + method
            + '('
            + ', '.join(args)
            + (', ' if args and kwargs else '')
            + ', '.join([f'{k}={v}' for k, v in kwargs.items()])
            + '): status='
            + str(response.status_code)
            + ', message='
            + getattr(response, 'meta', {}).get('message', '[No message]')
            + ', data='
            + str(response.json_data)
        )

        return response.json_data

    def _get_activities(
        self,
        since: Optional[str] = None,
        limit: Optional[int] = 25,
        object_type: Optional[str] = None,
        object_id: Optional[int] = None,
        sort: str = 'desc',
        **server_args,
    ) -> List[dict]:
        return self._execute(
            server_args,
            'get_activities',
            since=since,
            limit=limit,
            object_type=object_type,
            object_id=object_id,
            sort=sort,
        )

    @action
    def get_activities(
        self,
        since: Optional[str] = None,
        limit: Optional[int] = 25,
        object_type: Optional[str] = None,
        object_id: Optional[int] = None,
        sort: str = 'desc',
        **server_args,
    ) -> List[dict]:
        """
        Get the list of recent activities on an instance.

        :param since: Only return the activities that have occurred since the
            specified ID.
        :param limit: Maximum number of activities to be returned (default: 25).
        :param object_type: Filter by object type.
        :param object_id: Only get the activities related to a specific
            ``object_id``.
        :param sort: Sort mode, ``asc`` for ascending, ``desc`` for descending
            (default: ``desc``).
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        :return: The list of selected activities.
        """
        return self._get_activities(
            since=since,
            limit=limit,
            object_type=object_type,
            object_id=object_id,
            sort=sort,
            **server_args,
        )

    @action
    def get_apps(self, **server_args) -> List[str]:
        """
        Get the list of apps installed on a NextCloud instance.

        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        :return: The list of installed apps as strings.
        """
        return self._execute(server_args, 'get_apps').get('apps', [])

    @action
    def enable_app(self, app_id: Union[str, int], **server_args):
        """
        Enable an app.

        :param app_id: App ID.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(server_args, 'enable_app', app_id)

    @action
    def disable_app(self, app_id: Union[str, int], **server_args):
        """
        Disable an app.

        :param app_id: App ID.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(server_args, 'disable_app', app_id)

    @action
    def get_app(self, app_id: Union[str, int], **server_args) -> dict:
        """
        Provides information about an application.

        :param app_id: App ID.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        return self._execute(server_args, 'get_app', app_id)

    @action
    def get_capabilities(self, **server_args) -> dict:
        """
        Returns the capabilities of the server.

        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        :return: Server capabilities. Example:

          .. code-block:: json

            {
              "version": {
                "major": 27,
                "minor": 1,
                "micro": 5,
                "string": "27.1.5",
                "edition": "",
                "extendedSupport": false
              },
              "capabilities": {
                "core": {
                  "pollinterval": 60,
                  "webdav-root": "remote.php/webdav",
                },
                "files": {
                  "bigfilechunking": true,
                  "blacklisted_files": [
                    ".htaccess"
                  ],
                  "comments": true,
                  "undelete": true,
                  "versioning": true,
                  "version_labeling": true,
                  "version_deletion": true
                },
                "activity": {
                  "apiv2": [
                    "filters",
                    "filters-api",
                    "previews",
                    "rich-strings"
                  ]
                },
                "notifications": {
                  "ocs-endpoints": [
                    "list",
                    "get",
                    "delete",
                    "delete-all",
                    "icons",
                    "rich-strings",
                    "action-web",
                    "user-status",
                    "exists"
                  ],
                  "push": [
                    "devices",
                    "object-data",
                    "delete"
                  ],
                  "admin-notifications": [
                    "ocs",
                    "cli"
                  ]
                },
                "theming": {
                  "name": "Nextcloud",
                  "url": "https://nextcloud.com",
                  "slogan": "a safe home for all your data",
                  "color": "#1F5C98",
                  "color-text": "#ffffff",
                  "color-element": "#1F5C98",
                  "color-element-bright": "#1F5C98",
                  "color-element-dark": "#1F5C98",
                  "logo": "https://cloud.example.com/core/img/logo/logo.svg?v=0",
                  "background": "#1F5C98",
                  "background-plain": true,
                  "background-default": true,
                  "logoheader": "https://cloud.example.com/core/img/logo/logo.svg?v=0",
                  "favicon": "https://cloud.example.com/core/img/logo/logo.svg?v=0"
                },
                "user_status": {
                  "enabled": true,
                  "restore": true,
                  "supports_emoji": true
                },
              }
            }

        """
        return self._execute(server_args, 'get_capabilities')

    @action
    def add_group(self, group_id: Union[str, int], **server_args):
        """
        Create a new group.

        :param group_id: New group unique ID.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(server_args, 'add_group', group_id)

    @action
    def delete_group(self, group_id: Union[str, int], **server_args):
        """
        Delete a group.

        :param group_id: Group ID.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(server_args, 'delete_group', group_id)

    @action
    def get_group(self, group_id: Union[str, int], **server_args) -> dict:
        """
        Get the information of a group.

        :param group_id: Group ID.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        return self._execute(server_args, 'get_group', group_id)

    @action
    def get_groups(
        self,
        search: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **server_args,
    ) -> List[str]:
        """
        Search for groups.

        :param search: Search for groups matching the specified substring.
        :param limit: Maximum number of returned entries.
        :param offset: Start offset.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        return self._execute(
            server_args, 'get_groups', search=search, limit=limit, offset=offset
        ).get('groups', [])

    @action
    def create_group_folder(self, name: str, **server_args):
        """
        Create a new group folder.

        :param name: Name/path of the folder.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(server_args, 'create_group_folder', name)

    @action
    def delete_group_folder(self, folder_id: Union[int, str], **server_args):
        """
        Delete a new group folder.

        :param folder_id: Folder ID.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(server_args, 'delete_group_folder', folder_id)

    @action
    def get_group_folder(self, folder_id: Union[int, str], **server_args) -> dict:
        """
        Get a new group folder.

        :param folder_id: Folder ID.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        return self._execute(server_args, 'get_group_folder', folder_id)

    @action
    def get_group_folders(self, **server_args) -> List:
        """
        Get the list new group folder.

        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        return self._execute(server_args, 'get_group_folders')

    @action
    def rename_group_folder(
        self, folder_id: Union[int, str], new_name: str, **server_args
    ):
        """
        Rename a group folder.

        :param folder_id: Folder ID.
        :param new_name: New folder name.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(server_args, 'rename_group_folder', folder_id, new_name)

    @action
    def grant_access_to_group_folder(
        self, folder_id: Union[int, str], group_id: str, **server_args
    ):
        """
        Grant access to a group folder to a given group.

        :param folder_id: Folder ID.
        :param group_id: Group ID.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(server_args, 'grant_access_to_group_folder', folder_id, group_id)

    @action
    def revoke_access_to_group_folder(
        self, folder_id: Union[int, str], group_id: str, **server_args
    ):
        """
        Revoke access to a group folder to a given group.

        :param folder_id: Folder ID.
        :param group_id: Group ID.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(server_args, 'revoke_access_to_group_folder', folder_id, group_id)

    @action
    def set_group_folder_quota(
        self, folder_id: Union[int, str], quota: Optional[int], **server_args
    ):
        """
        Set the quota of a group folder.

        :param folder_id: Folder ID.
        :param quota: Quota in bytes - set None for unlimited.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(
            server_args,
            'set_quota_of_group_folder',
            folder_id,
            quota if quota is not None else -3,
        )

    @action
    def set_group_folder_permissions(
        self,
        folder_id: Union[int, str],
        group_id: str,
        permissions: List[str],
        **server_args,
    ):
        """
        Set the permissions on a folder for a group.

        :param folder_id: Folder ID.
        :param group_id: Group ID.
        :param permissions: New permissions, as a list including any of the
            following:

              - ``read``
              - ``update``
              - ``create``
              - ``delete``
              - ``share``
              - ``all``

        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(
            server_args,
            'set_permissions_to_group_folder',
            folder_id,
            group_id,
            self._get_permissions(permissions),
        )

    @action
    def get_notifications(self, **server_args) -> List[dict]:
        """
        Get the list of notifications for the logged user.

        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        :return: A list of notifications. Example:

          .. code-block:: json

            [
              {
                "notification_id": 1234,
                "app": "updatenotification",
                "user": "username",
                "datetime": "2024-01-01T19:00:00+00:00",
                "object_type": "side_menu",
                "object_id": "1.2.3",
                "subject": "Update for MyApp to version 1.2.3 is available.",
                "message": "",
                "link": "https://cloud.example.com/index.php/settings/apps/updates#myapp",
                "subjectRich": "Update for {app} to version 1.2.3 is available.",
                "subjectRichParameters": {
                  "app": {
                    "type": "app",
                    "id": "myapp",
                    "name": "MyApp"
                  }
                },
                "messageRich": "",
                "messageRichParameters": [],
                "icon": "https://cloud.example.com/apps/updatenotification/img/notification.svg",
                "shouldNotify": true,
                "actions": []
              }
            ]

        """
        return self._execute(server_args, 'get_notifications')

    @action
    def delete_notifications(self, **server_args):
        """
        Delete all notifications for the logged user.

        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(server_args, 'delete_all_notifications')

    @action
    def get_notification(self, notification_id: int, **server_args) -> dict:
        """
        Get the content of a notification.

        :param notification_id: Notification ID.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        :return: Notification details. Example:

          .. code-block:: json

              {
                "notification_id": 1234,
                "app": "updatenotification",
                "user": "username",
                "datetime": "2024-01-01T19:00:00+00:00",
                "object_type": "side_menu",
                "object_id": "1.2.3",
                "subject": "Update for MyApp to version 1.2.3 is available.",
                "message": "",
                "link": "https://cloud.example.com/index.php/settings/apps/updates#myapp",
                "subjectRich": "Update for {app} to version 1.2.3 is available.",
                "subjectRichParameters": {
                  "app": {
                    "type": "app",
                    "id": "myapp",
                    "name": "MyApp"
                  }
                },
                "messageRich": "",
                "messageRichParameters": [],
                "icon": "https://cloud.example.com/apps/updatenotification/img/notification.svg",
                "shouldNotify": true,
                "actions": []
              }

        """
        return self._execute(server_args, 'get_notification', notification_id)

    @action
    def delete_notification(self, notification_id: int, **server_args):
        """
        Delete a notification.

        :param notification_id: Notification ID.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(server_args, 'delete_notification', notification_id)

    @action
    def create_share(
        self,
        path: str,
        share_type: str,
        share_with: Optional[str] = None,
        public_upload: bool = False,
        password: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        **server_args,
    ) -> dict:
        """
        Share a file/folder with a user/group or a public link.

        :param path: Path to the resource to be shared.
        :param share_type: Share type. Supported values:

          - ``user``
          - ``group``
          - ``public_link``
          - ``email``
          - ``federated_cloud_share``
          - ``circle``
          - ``talk_conversation``

        :param share_with: User/group ID, email or conversation ID the resource
            should be shared with.
        :param public_upload: Whether public upload to the shared folder is
            allowed (default: False).
        :param password: Optional password to protect the share.
        :param permissions: Share permissions, as a list including any of the
            following (default: ``read``):

              - ``read``
              - ``update``
              - ``create``
              - ``delete``
              - ``share``
              - ``all``

        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        :return: The details of the newly created share. Example:

          .. code-block:: json

            {
              "id": "4",
              "share_type": 3,
              "uid_owner": "your_uid",
              "displayname_owner": "Your Name",
              "permissions": 17,
              "can_edit": true,
              "can_delete": true,
              "stime": 1599691325,
              "parent": null,
              "expiration": null,
              "token": "AbCdEfG0123456789",
              "uid_file_owner": "your_uid",
              "note": "",
              "label": "",
              "displayname_file_owner": "Your Name",
              "path": "/Shared Path",
              "item_type": "folder",
              "mimetype": "httpd/unix-directory",
              "storage_id": "home::your-uid",
              "storage": 2,
              "item_source": 13960,
              "file_source": 13960,
              "file_parent": 6,
              "file_target": "/Shared Path",
              "share_with": null,
              "share_with_displayname": "(Shared link)",
              "password": null,
              "send_password_by_talk": false,
              "url": "https://your-domain/nextcloud/index.php/s/AbCdEfG0123456789",
              "mail_send": 1,
              "hide_download": 0
            }

        """
        share_type_id = self._get_share_type(share_type)
        permissions_id = self._get_permissions(permissions or ['read'])
        return self._execute(
            server_args,
            'create_share',
            path,
            share_type=share_type_id,
            share_with=share_with,
            public_upload=public_upload,
            password=password,
            permissions=permissions_id,
        )

    @action
    def get_shares(self, **server_args) -> List[dict]:
        """
        Get the list of shares available on the server.

        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        :return: List of available shares. Example:

          .. code-block:: json

            [
                {
                  "id": "4",
                  "share_type": 3,
                  "uid_owner": "your_uid",
                  "displayname_owner": "Your Name",
                  "permissions": 17,
                  "can_edit": true,
                  "can_delete": true,
                  "stime": 1599691325,
                  "parent": null,
                  "expiration": null,
                  "token": "AbCdEfG0123456789",
                  "uid_file_owner": "your_uid",
                  "note": "",
                  "label": "",
                  "displayname_file_owner": "Your Name",
                  "path": "/Shared Path",
                  "item_type": "folder",
                  "mimetype": "httpd/unix-directory",
                  "storage_id": "home::your-uid",
                  "storage": 2,
                  "item_source": 13960,
                  "file_source": 13960,
                  "file_parent": 6,
                  "file_target": "/Shared Path",
                  "share_with": null,
                  "share_with_displayname": "(Shared link)",
                  "password": null,
                  "send_password_by_talk": false,
                  "url": "https://your-domain/nextcloud/index.php/s/AbCdEfG0123456789",
                  "mail_send": 1,
                  "hide_download": 0
                }
            ]

        """
        return self._execute(server_args, 'get_shares')

    @action
    def delete_share(self, share_id: int, **server_args):
        """
        Remove the shared state of a resource.

        :param share_id: Share ID.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(server_args, 'delete_share', str(share_id))

    @action
    def get_share(self, share_id: int, **server_args) -> dict:
        """
        Get the information of a shared resource.

        :param share_id: Share ID.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        :return: The details of the share. Example:

          .. code-block:: json

              {
                "id": "4",
                "share_type": 3,
                "uid_owner": "your_uid",
                "displayname_owner": "Your Name",
                "permissions": 17,
                "can_edit": true,
                "can_delete": true,
                "stime": 1599691325,
                "parent": null,
                "expiration": null,
                "token": "AbCdEfG0123456789",
                "uid_file_owner": "your_uid",
                "note": "",
                "label": "",
                "displayname_file_owner": "Your Name",
                "path": "/Shared Path",
                "item_type": "folder",
                "mimetype": "httpd/unix-directory",
                "storage_id": "home::your-uid",
                "storage": 2,
                "item_source": 13960,
                "file_source": 13960,
                "file_parent": 6,
                "file_target": "/Shared Path",
                "share_with": null,
                "share_with_displayname": "(Shared link)",
                "password": null,
                "send_password_by_talk": false,
                "url": "https://your-domain/nextcloud/index.php/s/AbCdEfG0123456789",
                "mail_send": 1,
                "hide_download": 0
              }

        """
        return self._execute(server_args, 'get_share_info', str(share_id))

    @action
    def update_share(
        self,
        share_id: int,
        public_upload: Optional[bool] = None,
        password: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        expire_date: Optional[str] = None,
        **server_args,
    ):
        """
        Update the permissions of a shared resource.

        :param share_id: Share ID.
        :param public_upload: Whether public upload to the shared folder is
            allowed (default: False).
        :param password: Optional password to protect the share.
        :param permissions: Share permissions, as a list including any of the
            following (default: ``read``):

              - ``read``
              - ``update``
              - ``create``
              - ``delete``
              - ``share``
              - ``all``

        :param expire_date: Share expiration date, in the format ``YYYY-MM-DD``.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        perms = self._get_permissions(permissions) if permissions else None
        self._execute(
            server_args,
            'update_share',
            share_id,
            public_upload=public_upload,
            password=password,
            permissions=perms,
            expire_date=expire_date,
        )

    @action
    def create_user(self, user_id: str, password: str, **server_args):
        """
        Create a user.

        :param user_id: User ID/name.
        :param password: User password
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(server_args, 'add_user', user_id, password)

    @action
    def edit_user(self, user_id: str, properties: Dict[str, str], **server_args):
        """
        Update a set of properties of a user.

        :param user_id: User ID/name.
        :param properties: Key-value pair of user attributes to be edited.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        for k, v in properties.items():
            self._execute(server_args, 'edit_user', user_id, k, v)

    @action
    def get_user(self, user_id: str, **server_args) -> dict:
        """
        Get the details of a user.

        :param user_id: User ID/name.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        :return: User details. Example:

          .. code-block:: json

            {
              "enabled": true,
              "storageLocation": "/mnt/hd/nextcloud/user",
              "id": "user",
              "lastLogin": 1599693750000,
              "backend": "Database",
              "subadmin": [],
              "quota": {
                "free": 6869434515456,
                "used": 1836924441,
                "total": 6871271439897,
                "relative": 0.03,
                "quota": -3
              },
              "email": "info@yourdomain.com",
              "displayname": "Your Name",
              "phone": "+1234567890",
              "address": "",
              "website": "https://yourdomain.com",
              "twitter": "@You",
              "groups": [
                "admin"
              ],
              "language": "en",
              "locale": "",
              "backendCapabilities": {
                "setDisplayName": true,
                "setPassword": true
              }
            }

        """
        return self._execute(server_args, 'get_user', user_id)

    @action
    def get_users(
        self,
        search: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **server_args,
    ) -> List[str]:
        """
        Get the list of users matching some search criteria.

        :param search: Return users matching the provided string.
        :param limit: Maximum number of results to be returned (default: no
            limit).
        :param offset: Search results offset (default: None).
        :return: List of the matched user IDs. Example:

            .. code-block:: json

                [
                    {
                      "enabled": true,
                      "storageLocation": "/mnt/hd/nextcloud/user",
                      "id": "user",
                      "lastLogin": 1599693750000,
                      "backend": "Database",
                      "subadmin": [],
                      "quota": {
                        "free": 6869434515456,
                        "used": 1836924441,
                        "total": 6871271439897,
                        "relative": 0.03,
                        "quota": -3
                      },
                      "email": "info@yourdomain.com",
                      "displayname": "Your Name",
                      "phone": "+1234567890",
                      "address": "",
                      "website": "https://yourdomain.com",
                      "twitter": "@You",
                      "groups": [
                        "admin"
                      ],
                      "language": "en",
                      "locale": "",
                      "backendCapabilities": {
                        "setDisplayName": true,
                        "setPassword": true
                      }
                    }
                ]

        """
        return self._execute(
            server_args, 'get_users', search=search, limit=limit, offset=offset
        )

    @action
    def delete_user(self, user_id: str, **server_args):
        """
        Delete a user.

        :param user_id: User ID/name.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(server_args, 'delete_user', user_id)

    @action
    def enable_user(self, user_id: str, **server_args):
        """
        Enable a user.

        :param user_id: User ID/name.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(server_args, 'enable_user', user_id)

    @action
    def disable_user(self, user_id: str, **server_args):
        """
        Disable a user.

        :param user_id: User ID/name.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(server_args, 'disable_user', user_id)

    @action
    def add_to_group(self, user_id: str, group_id: str, **server_args):
        """
        Add a user to a group.

        :param user_id: User ID/name.
        :param group_id: Group ID.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(server_args, 'add_to_group', user_id, group_id)

    @action
    def remove_from_group(self, user_id: str, group_id: str, **server_args):
        """
        Remove a user from a group.

        :param user_id: User ID/name.
        :param group_id: Group ID.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(server_args, 'remove_from_group', user_id, group_id)

    @action
    def create_subadmin(self, user_id: str, group_id: str, **server_args):
        """
        Add a user as a subadmin for a group.

        :param user_id: User ID/name.
        :param group_id: Group ID.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(server_args, 'create_subadmin', user_id, group_id)

    @action
    def remove_subadmin(self, user_id: str, group_id: str, **server_args):
        """
        Remove a user as a subadmin from a group.

        :param user_id: User ID/name.
        :param group_id: Group ID.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(server_args, 'remove_subadmin', user_id, group_id)

    @action
    def get_subadmin_groups(self, user_id: str, **server_args) -> List[str]:
        """
        Get the groups where a given user is subadmin.

        :param user_id: User ID/name.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        :return: List of matched groups as strings.
        """
        return self._execute(server_args, 'get_subadmin_groups', user_id)

    @action
    def create_folder(self, path: str, **server_args):
        """
        Create a folder.

        :param path: Path to the folder.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(server_args, 'create_folder', path)

    @action
    def mkdir(self, path: str, **server_args):
        """
        Alias for :meth:`.create_folder`.

        :param path: Path to the folder.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self.create_folder(path, **server_args)

    @action
    def delete(self, path: str, **server_args):
        """
        Delete a file or folder.

        :param path: Path to the resource.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(server_args, 'delete_path', path)

    @action
    def upload_file(
        self,
        remote_path: str,
        local_path: Optional[str] = None,
        content: Optional[str] = None,
        timestamp: Optional[Union[datetime, int, str]] = None,
        **server_args,
    ):
        """
        Upload a file.

        :param remote_path: Path to the remote resource.
        :param local_path: If set, identifies the path to the local file to be
            uploaded.
        :param content: If set, create a new file with this content instead of
            uploading an existing file.
        :param timestamp: File timestamp. If not specified it will be retrieved
            from the file info or set to ``now`` if ``content`` is specified.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        if isinstance(timestamp, datetime):
            timestamp = int(timestamp.timestamp())

        assert (local_path or content) and not (
            local_path and content
        ), 'Please specify either local_path or content'

        if local_path:
            method = 'upload_file'
            local_path = os.path.abspath(os.path.expanduser(local_path))
        else:
            method = 'upload_file_contents'

        return self._execute(
            server_args,
            method,
            local_path or content,
            remote_path,
            timestamp=timestamp,
        )

    @action
    def download_file(
        self,
        remote_path: str,
        local_path: str,
        **server_args,
    ):
        """
        Download a file.

        :param remote_path: Path to the remote resource.
        :param local_path: Path to the local folder.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        local_path = os.path.abspath(os.path.expanduser(local_path))
        cur_dir = os.getcwd()

        try:
            os.chdir(local_path)
            return self._execute(server_args, 'download_file', remote_path)
        finally:
            os.chdir(cur_dir)

    @action
    def list(
        self,
        path: str,
        depth: int = 1,
        all_properties: bool = False,
        **server_args,
    ) -> List[dict]:
        """
        List the content of a folder on the NextCloud instance.

        :param path: Remote path.
        :param depth: Search depth (default: 1).
        :param all_properties: Return all the file properties available
            (default: ``False``).
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        return self._execute(
            server_args,
            'list_folders',
            path,
            depth=depth,
            all_properties=all_properties,
        )

    @action
    def list_favorites(self, path: Optional[str] = None, **server_args) -> List[dict]:
        """
        List the favorite items for a user.

        :param path: Return only the favorites under this path.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        return self._execute(server_args, 'list_folders', path)

    @action
    def mark_favorite(self, path: Optional[str] = None, **server_args):
        """
        Add a path to a user's favorites.

        :param path: Resource path.
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(server_args, 'set_favorites', path)

    @action
    def copy(
        self,
        path: str,
        destination: str,
        overwrite: bool = False,
        **server_args,
    ):
        """
        Copy a resource to another path.

        :param path: Resource path.
        :param destination: Destination path.
        :param overwrite: Set to ``True`` if you want to overwrite any existing
            file (default: ``False``).
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(server_args, 'copy_path', path, destination, overwrite=overwrite)

    @action
    def move(
        self,
        path: str,
        destination: str,
        overwrite: bool = False,
        **server_args,
    ):
        """
        Move a resource to another path.

        :param path: Resource path.
        :param destination: Destination path.
        :param overwrite: Set to ``True`` if you want to overwrite any existing
            file (default: ``False``).
        :param server_args: Override the default server settings (see
            :meth:`._get_client` arguments).
        """
        self._execute(server_args, 'move_path', path, destination, overwrite=overwrite)

    def main(self):
        while not self.should_stop():
            last_seen_id = self.last_seen_id
            new_last_seen_id = last_seen_id
            activities = self._get_activities(
                sort='desc',
                url=self.conf.url,
                username=self.conf.username,
                password=self.conf.password,
                limit=100,
            )

            events = []
            for activity in activities:
                activity_id = int(activity['activity_id'])
                if last_seen_id and activity_id <= last_seen_id:
                    break

                events.append(self._activity_to_event(activity))

                if not new_last_seen_id or activity_id > new_last_seen_id:
                    new_last_seen_id = activity_id

            for evt in events[::-1]:
                self._bus.post(evt)

            if new_last_seen_id and last_seen_id != new_last_seen_id:
                self.last_seen_id = new_last_seen_id

            self.wait_stop(self.poll_interval)


# vim:sw=4:ts=4:et:
