import logging

logger = logging.getLogger('platypush')


def exec_wrapper(f, *args, **kwargs):
    from platypush import Response

    try:
        ret = f(*args, **kwargs)
        if isinstance(ret, Response):
            return ret

        return Response(output=ret)
    except Exception as e:
        logger.exception(e)
        return Response(errors=[str(e)])
