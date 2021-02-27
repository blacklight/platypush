from functools import wraps
from logging import getLogger

from platypush.common import exec_wrapper

logger = getLogger(__name__)


def cron(cron_expression: str):
    def wrapper(f):
        f.cron = True
        f.cron_expression = cron_expression

        @wraps(f)
        def wrapped(*args, **kwargs):
            return exec_wrapper(f, *args, **kwargs)

        return wrapped

    return wrapper


# vim:sw=4:ts=4:et:
