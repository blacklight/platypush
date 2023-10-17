from base64 import b64encode
import json
import subprocess
import threading
import time
from typing import Callable, Optional
from uuid import uuid1

from platypush.common.cmd_stream import redis_topic
from platypush.plugins import Plugin, action
from platypush.utils import get_redis


class ShellPlugin(Plugin):
    """
    Plugin to run shell commands.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _exec(self, func: Callable, cmd: str, ignore_errors: bool = False):
        try:
            return func(cmd)
        except subprocess.CalledProcessError as e:
            if ignore_errors:
                self.logger.warning(
                    'Command %s failed with error: %s', cmd, e.output.decode()
                )
                return None

            raise RuntimeError(e.output.decode()) from e

    def _exec_simple(self, cmd: str):
        return subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, shell=True
        ).decode()

    @staticmethod
    def _send_ws_output(cmd_id: str, buf: Optional[bytes]):
        get_redis().publish(
            redis_topic,
            json.dumps(
                {
                    'id': cmd_id,
                    'output': (b64encode(buf).decode() if buf is not None else None),
                }
            ),
        )

    def _exec_ws_thread(self, cmd: str, cmd_id: str):
        try:
            with subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
            ) as proc:
                first_loop = True

                while proc.poll() is None and proc.stdout and proc.stdout.readable():
                    buf = b''
                    bufsize = 1024

                    while len(buf) < bufsize:
                        ch = proc.stdout.read(1)
                        if not ch:
                            break

                        buf += ch
                        if ch in (b'\r', b'\n'):
                            break

                    if first_loop:
                        first_loop = False
                        # An artificial delay to let the client connect to the websocket,
                        # otherwise the first few lines of output might be lost.
                        time.sleep(2)

                    self._send_ws_output(cmd_id, buf)
        finally:
            self._send_ws_output(cmd_id, None)

    def _exec_ws(self, cmd: str):
        cmd_id = str(uuid1())
        threading.Thread(target=self._exec_ws_thread, args=(cmd, cmd_id)).start()
        return {'ws_path': f'/ws/shell?id={cmd_id}'}

    @action
    def exec(
        self,
        cmd: str,
        background: bool = False,
        ws: bool = False,
        ignore_errors: bool = False,
    ):
        """
        Run a command.

        :param cmd: Command to execute
        :param background: If set to True, execute the process in the
            background, otherwise wait for the process termination and return
            its output (default: False).
        :param ignore_errors: If set, then any errors in the command execution
            will be ignored. Otherwise a RuntimeError will be thrown (default
            value: False)
        :param ws: If set to True then the output of the command will be
            sent asynchronously over a websocket channel (default: False).
            In this case, the method will return a response in the format:

                .. code-block:: json

                    {
                        "ws_path": "/ws/shell?id=<cmd_id>"
                    }

            Where ``ws_path`` is the websocket path where the output of the
            command will be sent. The websocket will be closed when the command
            terminates.

        :returns: A response object where the ``output`` field will contain the
            command output as a string, and the ``errors`` field will contain
            whatever was sent to stderr.
        """
        if background:
            subprocess.Popen(cmd, shell=True)
            return None

        func = self._exec_ws if ws else self._exec_simple
        return self._exec(func, cmd, ignore_errors=ignore_errors)


# vim:sw=4:ts=4:et:
