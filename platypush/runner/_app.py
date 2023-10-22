import logging
import os
import signal
import subprocess
import sys
import time

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

    def main(self):
        self.logger.info('Starting application...')
        app = None

        try:
            with subprocess.Popen(
                [sys.executable, '-m', 'platypush.app', *self.args],
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr,
            ) as app:
                app.wait()
        except KeyboardInterrupt:
            pass

        if app and app.poll() is None:
            app.terminate()

        wait_start = time.time()
        while app and app.poll() is None:
            if time.time() - wait_start > 5:
                self.logger.warning('Application did not terminate, killing it')
                app.kill()
                break

            time.sleep(0.1)

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
