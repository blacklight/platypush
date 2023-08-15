import logging
import os
import signal
import subprocess
import sys
from typing_extensions import override

from platypush.process import ControllableProcess


class ApplicationProcess(ControllableProcess):
    """
    Controllable process wrapper interface for the main application.
    """

    def __init__(self, *args: str, pidfile: str, **kwargs):
        super().__init__(name='platypush', **kwargs)

        self.logger = logging.getLogger('platypush')
        self.args = args
        self.pidfile = pidfile

    def __enter__(self) -> "ApplicationProcess":
        self.start()
        return self

    def __exit__(self, *_, **__):
        self.stop()

    @override
    def main(self):
        self.logger.info('Starting application...')

        with subprocess.Popen(
            ['python', '-m', 'platypush.app', *self.args],
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
        ) as app:
            try:
                app.wait()
            except KeyboardInterrupt:
                pass

    @override
    def on_stop(self):
        try:
            with open(self.pidfile, 'r') as f:
                pid = int(f.read().strip())
        except (OSError, ValueError):
            pid = None

        if not pid:
            return

        try:
            os.kill(pid, signal.SIGINT)
        except OSError:
            pass
