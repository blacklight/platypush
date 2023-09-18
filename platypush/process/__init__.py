from abc import ABC, abstractmethod
import logging
from multiprocessing import Event, Process, RLock
from os import getpid
from typing import Optional


class ControllableProcess(Process, ABC):
    """
    Extends the ``Process`` class to allow for external extended control of the
    underlying process.
    """

    _kill_timeout: float = 10.0

    def __init__(self, *args, timeout: Optional[float] = None, **kwargs):
        kwargs['name'] = kwargs.get('name', self.__class__.__name__)
        super().__init__(*args, **kwargs)

        self.timeout = timeout
        self.logger = logging.getLogger(self.name)
        self._should_stop = Event()
        self._stop_lock = RLock()
        self._should_restart = False

    @property
    def _timeout_err(self) -> TimeoutError:
        return TimeoutError(f'Process {self.name} timed out')

    @property
    def should_stop(self) -> bool:
        """
        :return: ``True`` if the process is scheduled for stop, ``False``
            otherwise.
        """
        return self._should_stop.is_set()

    def wait_stop(self, timeout: Optional[float] = None) -> None:
        """
        Waits for the process to stop.

        :param timeout: The maximum time to wait for the process to stop.
        """
        timeout = timeout if timeout is not None else self.timeout
        stopped = self._should_stop.wait(timeout=timeout)

        if not stopped:
            raise self._timeout_err

        if self.pid == getpid():
            return  # Prevent termination deadlock

        self.join(timeout=timeout)
        if self.is_alive():
            raise self._timeout_err

    def stop(self, timeout: Optional[float] = None) -> None:
        """
        Stops the process.

        :param timeout: The maximum time to wait for the process to stop.
        """
        timeout = timeout if timeout is not None else self._kill_timeout
        with self._stop_lock:
            self._should_stop.set()
            self.on_stop()

            try:
                if self.pid != getpid():
                    self.wait_stop(timeout=timeout)
            except TimeoutError:
                pass
            finally:
                self.terminate()

            try:
                if self.pid != getpid():
                    self.wait_stop(timeout=self._kill_timeout)
            except TimeoutError:
                self.logger.warning(
                    'The process %s is still alive after %f seconds, killing it',
                    self.name,
                    self._kill_timeout,
                )
                self.kill()

    def on_stop(self) -> None:
        """
        Handler called when the process is stopped.

        It can be implemented by subclasses.
        """

    @property
    def should_restart(self) -> bool:
        """
        :return: ``True`` if the process is marked for restart after stop,
            ``False`` otherwise.
        """
        return self._should_restart

    def mark_for_restart(self):
        """
        Marks the process for restart after stop.
        """
        self._should_restart = True

    @abstractmethod
    def main(self):
        """
        The main function of the process.

        It must be implemented by subclasses.
        """

    def _main(self):
        """
        Wrapper for the main function of the process.
        """
        self._should_restart = False
        return self.main()

    def run(self) -> None:
        """
        Executes the process.
        """
        super().run()

        try:
            self._main()
        finally:
            self._should_stop.set()
            self.logger.info('Process terminated')
