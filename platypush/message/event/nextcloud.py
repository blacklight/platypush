from platypush.message.event import Event


class NextCloudActivityEvent(Event):
    def __init__(self, activity_id: int, activity_type: str, *args, **kwargs):
        super().__init__(*args, activity_id=activity_id, activity_type=activity_type, **kwargs)


# vim:sw=4:ts=4:et:
