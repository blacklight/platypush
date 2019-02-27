from platypush.message.event import Event


class CameraEvent(Event):
    """ Base class for camera events """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CameraRecordingStartedEvent(CameraEvent):
    """
    Event triggered when a new recording starts
    """

    def __init__(self, device_id, filename=None, *args, **kwargs):
        super().__init__(*args, device_id=device_id, filename=filename, **kwargs)


class CameraRecordingStoppedEvent(CameraEvent):
    """
    Event triggered when a recording stops
    """

    def __init__(self, device_id, *args, **kwargs):
        super().__init__(*args, device_id=device_id, **kwargs)


class CameraVideoRenderedEvent(CameraEvent):
    """
    Event triggered when a sequence of frames has been rendered into a video
    """

    def __init__(self, filename=None, *args, **kwargs):
        super().__init__(*args, filename=filename, **kwargs)


class CameraPictureTakenEvent(CameraEvent):
    """
    Event triggered when a snapshot has been taken
    """

    def __init__(self, filename=None, *args, **kwargs):
        super().__init__(*args, filename=filename, **kwargs)


# vim:sw=4:ts=4:et:
