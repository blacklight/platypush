from platypush.message.event import Event


class PushbulletEvent(Event):
    """
    PushBullet event object.

    If you have configured the PushBullet backend with your account token,
    and enabled notification mirroring on the PushBullet app on your mobile
    devices, then the backend will trigger a PushbulletEvent whenever
    a new notiification hits your mobile, and you can react to that event
    through hooks that can, for example, log your notifications on a database,
    display them on a dashboard, let the built-in text-to-speech plugin read
    them out loud to you if they match the package name of your news app,
    display them on your smart watch if they are pictures, and so on.
    """

    def __init__(self, *args, **kwargs):
        """ Platypush supports by default the PushBullet notification mirror
            format, https://docs.pushbullet.com/#mirrored-notifications """

        if 'type' in kwargs:
            # Prevent name clash with event type attribute
            kwargs['push_type'] = kwargs.pop('type')

        super().__init__(*args, **kwargs)


# vim:sw=4:ts=4:et:

