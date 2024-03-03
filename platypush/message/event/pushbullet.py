from typing import Optional, Union

from platypush.message.event import Event


class PushbulletEvent(Event):
    """
    Base PushBullet event.
    """

    def __init__(
        self,
        *args,
        notification_id: str,
        title: Optional[str] = None,
        body: Optional[Union[str, dict, list]] = None,
        url: Optional[str] = None,
        source_device: Optional[str] = None,
        source_user: Optional[str] = None,
        target_device: Optional[str] = None,
        icon: Optional[str] = None,
        created: float,
        modified: float,
        **kwargs
    ):
        """
        :param notification_id: Notification ID.
        :param title: Notification title.
        :param body: Notification body.
        :param url: Notification URL.
        :param source_device: Source device ID.
        :param source_user: Source user ID.
        :param target_device: Target device ID.
        :param icon: Notification icon.
        :param created: Notification creation timestamp.
        :param modified: Notification modification timestamp.
        :param kwargs: Additional attributes.
        """
        super().__init__(
            *args,
            notification_id=notification_id,
            title=title,
            body=body,
            url=url,
            source_device=source_device,
            source_user=source_user,
            target_device=target_device,
            icon=icon,
            created=created,
            modified=modified,
            **kwargs
        )


class PushbulletMessageEvent(PushbulletEvent):
    """
    Triggered when a new message is received.
    """

    def __init__(
        self,
        *args,
        sender_id: Optional[str] = None,
        sender_email: Optional[str] = None,
        sender_name: Optional[str] = None,
        receiver_id: Optional[str] = None,
        receiver_email: Optional[str] = None,
        receiver_name: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            *args,
            sender_id=sender_id,
            sender_email=sender_email,
            sender_name=sender_name,
            receiver_id=receiver_id,
            receiver_email=receiver_email,
            receiver_name=receiver_name,
            **kwargs
        )


class PushbulletNotificationEvent(PushbulletEvent):
    """
    Triggered when a notification is mirrored from another device.
    """

    def __init__(
        self,
        *args,
        title: str,
        body: str,
        dismissible: bool,
        application_name: Optional[str] = None,
        package_name: Optional[str] = None,
        actions: Optional[dict] = None,
        **kwargs
    ):
        """
        :param title: Mirror notification title.
        :param body: Mirror notification body.
        :param dismissible: True if the notification can be dismissed.
        :param application_name: Application name.
        :param package_name: Package name.
        :param actions: Actions associated to the notification. Example:

            .. code-block:: json

                [
                  {
                    "label": "previous",
                    "trigger_key": "com.termux.api_0_6107998_previous"
                  },
                  {
                    "label": "pause",
                    "trigger_key": "com.termux.api_0_6107998_pause"
                  },
                  {
                    "label": "play",
                    "trigger_key": "com.termux.api_0_6107998_play"
                  },
                  {
                    "label": "next",
                    "trigger_key": "com.termux.api_0_6107998_next"
                  }
                ]

        """
        super().__init__(
            *args,
            title=title,
            body=body,
            dismissible=dismissible,
            application_name=application_name,
            package_name=package_name,
            actions=actions,
            **kwargs
        )


class PushbulletDismissalEvent(PushbulletEvent):
    """
    Triggered when a notification is dismissed.
    """

    def __init__(self, *args, package_name: Optional[str] = None, **kwargs):
        super().__init__(*args, package_name=package_name, **kwargs)


class PushbulletLinkEvent(PushbulletMessageEvent):
    """
    Triggered when a push with a link is received.
    """


class PushbulletFileEvent(PushbulletMessageEvent):
    """
    Triggered when a push with a file is received.
    """

    def __init__(
        self,
        *args,
        file_name: str,
        file_type: str,
        file_url: str,
        image_width: Optional[int] = None,
        image_height: Optional[int] = None,
        image_url: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            *args,
            file_name=file_name,
            file_type=file_type,
            file_url=file_url,
            image_width=image_width,
            image_height=image_height,
            image_url=image_url,
            **kwargs
        )


# vim:sw=4:ts=4:et:
