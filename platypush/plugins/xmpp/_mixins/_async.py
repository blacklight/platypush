from abc import ABC, abstractmethod
import asyncio
import concurrent.futures
from typing import Callable, Coroutine, Optional

from .._types import Errors
from ._base import XmppBaseMixin


# pylint: disable=too-few-public-methods
class XmppAsyncMixin(XmppBaseMixin, ABC):
    """
    This mixin provides a common interface for aioxmpp's asyncio interface.
    """

    @abstractmethod
    def __init__(
        self, *args, loop: Optional[asyncio.AbstractEventLoop] = None, **kwargs
    ):
        self._loop = loop
        super().__init__(*args, **kwargs)

    def _async_run(
        self,
        coro: Callable[..., Coroutine],
        *args,
        timeout: Optional[float] = XmppBaseMixin.DEFAULT_TIMEOUT,
        wait_result: bool = True,
        **kwargs,
    ):
        """
        Utility method to call an async action from the thread of the parent
        action.
        """
        assert self._loop, Errors.LOOP
        fut = asyncio.run_coroutine_threadsafe(coro(*args, **kwargs), self._loop)

        if wait_result:
            err = None

            try:
                return fut.result(timeout)
            except (TimeoutError, concurrent.futures.TimeoutError) as e:
                self.logger.warning(
                    'Call to %s timed out after %f seconds', coro, timeout
                )
                err = e
            except Exception as e:
                self.logger.warning('Call to %s failed: %s', coro, e)
                self.logger.exception(e)
                err = e
            finally:
                assert not err, str(err)

        return None
