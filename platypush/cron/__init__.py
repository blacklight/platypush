from functools import wraps
from logging import getLogger

logger = getLogger(__name__)


def cron(cron_expression: str):
    def wrapper(f):
        f.cron = True
        f.cron_expression = cron_expression

        @wraps(f)
        def wrapped(*args, **kwargs):
            from platypush import Response

            try:
                ret = f(*args, **kwargs)
                if isinstance(ret, Response):
                    return ret

                return Response(output=ret)
            except Exception as e:
                logger.exception(e)
                return Response(errors=[str(e)])

        return wrapped

    return wrapper


# vim:sw=4:ts=4:et:
