import logging

from platypush.config import Config

_logger = None


def logger():
    global _logger
    if not _logger:
        log_args = {
            'level': logging.INFO,
            'format': '%(asctime)-15s|%(levelname)5s|%(name)s|%(message)s',
        }

        level = (Config.get('backend.http') or {}).get('logging') or (
            Config.get('logging') or {}
        ).get('level')
        filename = (Config.get('backend.http') or {}).get('filename')

        if level:
            log_args['level'] = (
                getattr(logging, level.upper()) if isinstance(level, str) else level
            )
        if filename:
            log_args['filename'] = filename

        logging.basicConfig(**log_args)
        _logger = logging.getLogger('platypush:web')

    return _logger
