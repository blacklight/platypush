from datetime import datetime as dt
from typing import Optional

from platypush.message.event import Event


class NextCloudActivityEvent(Event):
    """
    Event triggered when a new activity is detected on a NextCloud instance.
    """

    def __init__(
        self,
        *args,
        activity_id: int,
        activity_type: str,
        object_id: int,
        object_type: str,
        object_name: str,
        app: str,
        user: str,
        subject: str,
        message: str,
        subject_rich: Optional[list] = None,
        message_rich: Optional[list] = None,
        objects: Optional[dict] = None,
        link: Optional[str] = None,
        icon: Optional[str] = None,
        datetime: Optional[dt] = None,
        **kwargs,
    ):
        """
        :param activity_id: Activity ID.
        :param activity_type: Activity type - can be ``file_created``,
            ``file_deleted``, ``file_changed``, ``file_restored``,
            ``file_shared``, ``file_unshared``, ``file_downloaded``, etc.
        :param object_id: Object ID.
        :param object_type: Object type - can be files, comment, tag, share,
            etc.
        :param object_name: Object name. In the case of files, it's the file
            path relative to the user's root directory.
        :param app: Application that generated the activity.
        :param user: User that generated the activity.
        :param subject: Activity subject, in plain text. For example, *You
            created hd/test1.txt and hd/test2.txt*.
        :param message: Activity message, in plain text.
        :param subject_rich: Activity subject, in rich/structured format.
            Example:

              .. code-block:: json

                [
                  "You created {file2} and {file1}",
                  {
                    "file1": {
                      "type": "file",
                      "id": "1234",
                      "name": "test1.txt",
                      "path": "hd/text1.txt",
                      "link": "https://cloud.example.com/index.php/f/1234"
                    },
                    "file2": {
                      "type": "file",
                      "id": "1235",
                      "name": "test2.txt",
                      "path": "hd/text2.txt",
                      "link": "https://cloud.example.com/index.php/f/1235"
                    }
                  }
                ]

        :param message_rich: Activity message, in rich/structured format.
        :param objects: Additional objects associated to the activity, in the
            format ``{object_id: object}``. For example, if the activity
            involves files, the ``objects`` dictionary will contain the mapping
            of the involved files in the format ``{file_id: path}``.
        :param link: Link to the main object of this activity. Example:
            ``https://cloud.example.com/index.php/files/apps/files/?dir=/hd&fileid=1234``
        :param icon: URL of the icon associated to the activity.
        :param datetime: Activity timestamp.
        """
        super().__init__(
            *args,
            activity_id=activity_id,
            activity_type=activity_type,
            object_id=object_id,
            object_type=object_type,
            object_name=object_name,
            app=app,
            user=user,
            subject=subject,
            subject_rich=subject_rich,
            message=message,
            message_rich=message_rich,
            objects=objects or {},
            link=link,
            icon=icon,
            datetime=datetime,
            **kwargs,
        )


# vim:sw=4:ts=4:et:
