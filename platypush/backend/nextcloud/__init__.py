from typing import Optional

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message.event.nextcloud import NextCloudActivityEvent
from platypush.plugins.nextcloud import NextcloudPlugin
from platypush.plugins.variable import VariablePlugin


class NextcloudBackend(Backend):
    """
    This backend triggers events when new activities occur on a NextCloud instance.

    Triggers:

        - :class:`platypush.message.event.nextcloud.NextCloudActivityEvent` when new activity occurs on the instance.
          The field ``activity_type`` identifies the activity type (e.g. ``file_created``, ``file_deleted``,
          ``file_changed``). Example in the case of the creation of new files:

          .. code-block:: json

            {
              "activity_id": 387,
              "app": "files",
              "activity_type": "file_created",
              "user": "your-user",
              "subject": "You created InstantUpload/Camera/IMG_0100.jpg, InstantUpload/Camera/IMG_0101.jpg and InstantUpload/Camera/IMG_0102.jpg",
              "subject_rich": [
                "You created {file3}, {file2} and {file1}",
                {
                  "file1": {
                    "type": "file",
                    "id": "41994",
                    "name": "IMG_0100.jpg",
                    "path": "InstantUpload/Camera/IMG_0100.jpg",
                    "link": "https://your-domain/nextcloud/index.php/f/41994"
                  },
                  "file2": {
                    "type": "file",
                    "id": "42005",
                    "name": "IMG_0101.jpg",
                    "path": "InstantUpload/Camera/IMG_0102.jpg",
                    "link": "https://your-domain/nextcloud/index.php/f/42005"
                  },
                  "file3": {
                    "type": "file",
                    "id": "42014",
                    "name": "IMG_0102.jpg",
                    "path": "InstantUpload/Camera/IMG_0102.jpg",
                    "link": "https://your-domain/nextcloud/index.php/f/42014"
                  }
                }
              ],
              "message": "",
              "message_rich": [
                "",
                []
              ],
              "object_type": "files",
              "object_id": 41994,
              "object_name": "/InstantUpload/Camera/IMG_0102.jpg",
              "objects": {
                "42014": "/InstantUpload/Camera/IMG_0100.jpg",
                "42005": "/InstantUpload/Camera/IMG_0101.jpg",
                "41994": "/InstantUpload/Camera/IMG_0102.jpg"
              },
              "link": "https://your-domain/nextcloud/index.php/apps/files/?dir=/InstantUpload/Camera",
              "icon": "https://your-domain/nextcloud/apps/files/img/add-color.svg",
              "datetime": "2020-09-07T17:04:29+00:00"
            }

    """

    _LAST_ACTIVITY_VARNAME = '_NEXTCLOUD_LAST_ACTIVITY_ID'

    def __init__(self, url: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None,
                 object_type: Optional[str] = None, object_id: Optional[int] = None,
                 poll_seconds: Optional[float] = 60., **kwargs):
        """
        :param url: NextCloud instance URL (default: same as the :class:`platypush.plugins.nextcloud.NextCloudPlugin`).
        :param username: NextCloud username (default: same as the :class:`platypush.plugins.nextcloud.NextCloudPlugin`).
        :param password: NextCloud password (default: same as the :class:`platypush.plugins.nextcloud.NextCloudPlugin`).
        :param object_type: If set, only filter events on this type of object.
        :param object_id: If set, only filter events on this object ID.
        :param poll_seconds: How often the backend should poll the instance (default: one minute).
        """
        super().__init__(**kwargs)
        self.url: Optional[str] = None
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self.object_type = object_type
        self.object_id = object_id
        self.poll_seconds = poll_seconds
        self._last_seen_id = None

        try:
            plugin: Optional[NextcloudPlugin] = get_plugin('nextcloud')
            if plugin:
                self.url = plugin.conf.url
                self.username = plugin.conf.username
                self.password = plugin.conf.password
        except Exception as e:
            self.logger.info('NextCloud plugin not configured: {}'.format(str(e)))

        self.url = url if url else self.url
        self.username = username if username else self.username
        self.password = password if password else self.password

        assert self.url and self.username and self.password, \
            'No configuration provided neither for the NextCloud plugin nor the backend'

    @property
    def last_seen_id(self) -> Optional[int]:
        if self._last_seen_id is None:
            variables: VariablePlugin = get_plugin('variable')
            last_seen_id = variables.get(self._LAST_ACTIVITY_VARNAME).output.get(self._LAST_ACTIVITY_VARNAME)
            self._last_seen_id = last_seen_id

        return self._last_seen_id

    @last_seen_id.setter
    def last_seen_id(self, value: Optional[int]):
        variables: VariablePlugin = get_plugin('variable')
        variables.set(**{self._LAST_ACTIVITY_VARNAME: value})
        self._last_seen_id = value

    @staticmethod
    def _activity_to_event(activity: dict) -> NextCloudActivityEvent:
        return NextCloudActivityEvent(activity_type=activity.pop('type'), **activity)

    def loop(self):
        last_seen_id = int(self.last_seen_id)
        new_last_seen_id = int(last_seen_id)
        plugin: NextcloudPlugin = get_plugin('nextcloud')
        # noinspection PyUnresolvedReferences
        activities = plugin.get_activities(sort='desc', url=self.url, username=self.username, password=self.password,
                                           object_type=self.object_type, object_id=self.object_id).output

        events = []
        for activity in activities:
            if last_seen_id and activity['activity_id'] <= last_seen_id:
                break

            events.append(self._activity_to_event(activity))

            if not new_last_seen_id or activity['activity_id'] > new_last_seen_id:
                new_last_seen_id = int(activity['activity_id'])

        for evt in events[::-1]:
            self.bus.post(evt)

        if new_last_seen_id and last_seen_id != new_last_seen_id:
            self.last_seen_id = new_last_seen_id


# vim:sw=4:ts=4:et:
