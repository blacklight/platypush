from typing import Optional, Union

from platypush.message.event import Event


class ZeroborgEvent(Event):
    pass


class ZeroborgDriveEvent(ZeroborgEvent):
    def __init__(self, motors: Union[list, tuple], direction: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, motors=motors, direction=direction, **kwargs)


class ZeroborgStopEvent(ZeroborgEvent):
    pass


# vim:sw=4:ts=4:et:
