import logging
import sys
from threading import Thread
from typing import Optional

from platypush.cli import parse_cmdline
from platypush.commands import CommandStream

from ._app import ApplicationProcess


class ApplicationRunner:
    """
    Runner for the main application.

    It wraps the main application and provides an interface to control it
    externally.
    """

    _default_timeout = 0.5

    def __init__(self):
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
        self.logger = logging.getLogger('platypush:runner')
        self._proc: Optional[ApplicationProcess] = None

    def _listen(self, stream: CommandStream):
        """
        Listens for external application commands and executes them.
        """
        while self.is_running:
            cmd = stream.read(timeout=self._default_timeout)
            if not cmd:
                continue

            self.logger.info(cmd)
            Thread(target=cmd, args=(self,)).start()

    def _print_version(self):
        from platypush import __version__

        print(__version__)
        sys.exit(0)

    def _run(self, *args: str) -> None:
        parsed_args = parse_cmdline(args)

        if parsed_args.version:
            self._print_version()

        while True:
            with (
                CommandStream(parsed_args.ctrl_sock) as stream,
                ApplicationProcess(
                    *args, pidfile=parsed_args.pidfile, timeout=self._default_timeout
                ) as self._proc,
            ):
                try:
                    self._listen(stream)
                except KeyboardInterrupt:
                    pass

                if self.should_restart:
                    self.logger.info('Restarting application...')
                    continue

                break

    def run(self, *args: str) -> None:
        try:
            self._run(*args)
        finally:
            self._proc = None

    def stop(self):
        if self._proc is not None:
            self._proc.stop()

    def restart(self):
        if self._proc is not None:
            self._proc.mark_for_restart()

        self.stop()

    @property
    def is_running(self) -> bool:
        return bool(self._proc and self._proc.is_alive())

    @property
    def should_restart(self) -> bool:
        return self._proc.should_restart if self._proc is not None else False
