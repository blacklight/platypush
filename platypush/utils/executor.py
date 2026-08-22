import atexit
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

logger = logging.getLogger('platypush')

# Bounded worker counts for background request and bus work. These are
# conservative defaults meant to cap OS thread churn while still allowing
# reasonable concurrency for I/O-bound work.
_REQUEST_MAX_WORKERS = 20
_BUS_MAX_WORKERS = 20

_request_executor: Optional[ThreadPoolExecutor] = None
_bus_executor: Optional[ThreadPoolExecutor] = None
_executor_lock = threading.RLock()


def _get_or_create_executor(
    name: str,
    max_workers: int,
    thread_name_prefix: str,
    executor_ref: Optional[ThreadPoolExecutor],
) -> ThreadPoolExecutor:
    with _executor_lock:
        if executor_ref is None or getattr(executor_ref, '_shutdown', False):
            executor_ref = ThreadPoolExecutor(
                max_workers=max_workers, thread_name_prefix=thread_name_prefix
            )

            global _request_executor, _bus_executor
            if name == 'request':
                _request_executor = executor_ref
            else:
                _bus_executor = executor_ref

    return executor_ref


def get_request_executor() -> ThreadPoolExecutor:
    global _request_executor
    _request_executor = _get_or_create_executor(
        'request', _REQUEST_MAX_WORKERS, 'platypush-req', _request_executor
    )
    return _request_executor


def get_bus_executor() -> ThreadPoolExecutor:
    global _bus_executor
    _bus_executor = _get_or_create_executor(
        'bus', _BUS_MAX_WORKERS, 'platypush-bus', _bus_executor
    )
    return _bus_executor


def shutdown_executors(wait: bool = True):
    """
    Shut down the global request and bus executors.

    :param wait: If True, block until the pending work has completed. Use
        ``wait=False`` during process shutdown to avoid hanging on long-running
        tasks.
    """
    global _request_executor, _bus_executor
    with _executor_lock:
        for name, executor in (('request', _request_executor), ('bus', _bus_executor)):
            if executor is None:
                continue

            try:
                if not getattr(executor, '_shutdown', False):
                    logger.debug('Shutting down %s executor', name)
                    executor.shutdown(wait=wait)
            except Exception as e:
                logger.warning('Error shutting down %s executor: %s', name, e)
            finally:
                if name == 'request':
                    _request_executor = None
                else:
                    _bus_executor = None


atexit.register(shutdown_executors, wait=False)
