import logging
import os
import pytest
import time
from threading import Thread

from platypush import Daemon, Config

from .utils import config_file, set_base_url

app_start_timeout = 5


def clear_loggers():
    """
    Remove handlers from all loggers at teardown.
    This is to prevent pytest spitting out logging errors on teardown if the logging objects have been deinitialized
    (see https://github.com/pytest-dev/pytest/issues/5502#issuecomment-647157873).
    """
    import logging
    # noinspection PyUnresolvedReferences
    loggers = [logging.getLogger()] + list(logging.Logger.manager.loggerDict.values())
    for logger in loggers:
        handlers = getattr(logger, 'handlers', [])
        for handler in handlers:
            logger.removeHandler(handler)


@pytest.fixture(scope='session', autouse=True)
def app():
    logging.info('Starting Platypush test service')

    Config.init(config_file)
    app = Daemon(config_file=config_file, redis_queue='platypush-tests/bus')
    Thread(target=lambda: app.run()).start()
    logging.info('Sleeping {} seconds while waiting for the daemon to start up'.format(app_start_timeout))
    time.sleep(app_start_timeout)
    yield app

    logging.info('Stopping Platypush test service')
    app.stop_app()
    clear_loggers()
    db_file = (Config.get('main.db') or {}).get('engine', '')[len('sqlite:///'):]

    if db_file and os.path.isfile(db_file):
        logging.info('Removing temporary db file {}'.format(db_file))
        os.unlink(db_file)


@pytest.fixture(scope='session')
def db_file():
    yield Config.get('main.db')['engine'][len('sqlite:///'):]


@pytest.fixture(scope='session')
def base_url():
    backends = Config.get_backends()
    assert 'http' in backends, 'Missing HTTP server configuration'
    url = 'http://localhost:{port}'.format(port=backends['http']['port'])
    set_base_url(url)
    yield url
