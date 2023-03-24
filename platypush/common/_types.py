from abc import ABC, abstractmethod
from threading import Thread


class StoppableThread(Thread, ABC):
    """
    Base interface for stoppable threads.
    """

    @abstractmethod
    def stop(self):
        ...
