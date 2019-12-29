import threading

from abc import ABC, abstractmethod
from queue import Queue
from typing import Type


class EndOfStream:
    pass


class Worker(ABC, threading.Thread):
    """
    Generic class for worker threads, used to split the execution of an action over multiple
    parallel instances.
    """

    def __init__(self, request_queue: Queue, response_queue=Queue, id=None):
        """
        :param request_queue: The worker will listen for messages to process over this queue
        :param response_queue: The worker will return responses over this queue
        """
        super().__init__()
        self.request_queue = request_queue
        self.response_queue = response_queue
        self._id = id

    def run(self) -> None:
        """
        The worker will run until it receives a :class:`EndOfStream` message on the queue.
        """
        while True:
            msg = self.request_queue.get()
            if isinstance(msg, EndOfStream):
                break

            try:
                ret = self.process(msg)
            except Exception as e:
                ret = e

            if ret:
                # noinspection PyArgumentList,PyCallByClass
                self.response_queue.put(ret)

    @abstractmethod
    def process(self, msg):
        """
        This method must be implemented by the derived classes.
        It will take as argument a message received over the `request_queue` and will return a value that will be
        processed by the consumer or None.

        If this function raises an exception then the exception will be pushed to the response queue and can be
        handled by the consumer.
        """
        raise NotImplementedError('Must be implemented by a derived class')

    def end_stream(self) -> None:
        """
        This method will be called when we have no more messages to send to the worker. A special
        `EndOfStream` object will be sent on the `request_queue`.
        """
        self.request_queue.put(EndOfStream())


class Workers:
    """
    Model for a pool of workers. Syntax:

    .. code-block:: python

        class Squarer(Worker):
            def process(self, n):
                return n * n

        workers = Workers(5, Squarer)  # Allocate 5 workers of type Squarer
        with workers:
            for n in range(100)):
                workers.put(n)

        print(workers.responses)

    """

    def __init__(self, n_workers: int, worker_type: Type[Worker], *args, **kwargs):
        """
        :param n_workers: Number of workers
        :param worker_type: Type of the workers that will be instantiated. Must be a subclass of :class:`Worker`.
        :param args: Extra args to pass to the `worker_type` constructor
        :param kwargs: Extra kwargs to pass to the `worker_type` constructor
        """
        self.request_queue = Queue()
        self.response_queue = Queue()
        # noinspection PyArgumentList
        self._workers = [worker_type(self.request_queue, self.response_queue, id=i, *args, **kwargs)
                         for i in range(n_workers)]
        self.responses = []

    def start(self):
        for wrk in self._workers:
            wrk.start()

    def put(self, msg) -> None:
        """
        Put a message on the `request_queue`
        """
        self.request_queue.put(msg)

    def wait(self) -> list:
        """
        Wait for the termination of all the workers

        :ret: A list containing the processed responses
        """
        while self._workers:
            wrk = self._workers.pop()
            wrk.join()

        while not self.response_queue.empty():
            self.responses.append(self.response_queue.get())

        return self.responses

    def end_stream(self):
        """
        Mark the termination of the stream by sending an :class:`EndOfStream` message on the `request_queue` for
        each of the running workers.
        """
        for wrk in self._workers:
            wrk.end_stream()

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_stream()
        self.wait()


# vim:sw=4:ts=4:et:
