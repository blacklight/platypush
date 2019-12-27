from typing import Optional

from platypush.message.response import Response


class PingResponse(Response):
    # noinspection PyShadowingBuiltins
    def __init__(self,
                 host: str,
                 success: bool,
                 *args,
                 min: Optional[float] = None,
                 max: Optional[float] = None,
                 avg: Optional[float] = None,
                 mdev: Optional[float] = None,
                 **kwargs):
        super().__init__(*args, output={
            'host': host,
            'success': success,
            'min': min,
            'max': max,
            'avg': avg,
            'mdev': mdev,
        }, **kwargs)


# vim:sw=4:ts=4:et:
