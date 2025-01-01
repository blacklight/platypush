from platypush.plugins._actions import LoggedAction

from . import WSRoute


class WSMonitorProxy(WSRoute):
    """
    Websocket proxy for the action monitor, mapped to ``/ws/monitor``.
    """

    _monitor_channel = WSRoute.get_channel('monitor')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, subscriptions=[self._monitor_channel], **kwargs)

    @classmethod
    def app_name(cls) -> str:
        return 'monitor'

    @classmethod
    def publish(cls, data: LoggedAction, *_) -> None:  # type: ignore
        super().publish(data.dump(), cls._monitor_channel)

    def run(self) -> None:
        for msg in self.listen():
            self.send(msg.data)
