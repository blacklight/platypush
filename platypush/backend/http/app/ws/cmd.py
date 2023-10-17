from base64 import b64decode
import json
from typing import Optional

from platypush.common.cmd_stream import redis_topic

from . import WSRoute, logger


class WSCommandOutput(WSRoute):
    """
    Websocket route that pushes the output of an executed command to the client
    as it is generated. Mapped to ``/ws/shell``.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, subscriptions=[redis_topic], **kwargs)
        self._id = None

    @classmethod
    def app_name(cls) -> str:
        return 'shell'

    @classmethod
    def path(cls) -> str:
        return f'/ws/{cls.app_name()}'

    def _parse_msg(self, msg: bytes) -> Optional[bytes]:
        parsed_msg = json.loads(msg)
        cmd_id = parsed_msg.get('id')
        output = parsed_msg.get('output')
        if output is None:  # End-of-stream
            raise StopIteration()

        if cmd_id != self._id:
            return None

        return b64decode(output)

    def open(self, *args, **kwargs):
        self._id = next(iter(self.request.arguments['id']), b'').decode() or None
        super().open(*args, **kwargs)

    def run(self) -> None:
        super().run()
        for msg in self.listen():
            try:
                output = self._parse_msg(msg.data)
                if output is None:
                    continue

                self.send(output)
            except StopIteration:
                break
            except Exception as e:
                logger.warning('Failed to parse message: %s', e)
                logger.exception(e)
                continue

        self._io_loop.add_callback(self._ws_close)

    def _ws_close(self):
        if not self.ws_connection:
            return

        self.ws_connection.close(1000, 'Command terminated')
