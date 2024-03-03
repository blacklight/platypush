import logging
import os
import time
from threading import Thread

import pytest
import requests

from platypush import Application, Config

from .utils import config_file, set_base_url

app_start_timeout = 15


def clear_loggers():
    """
    Remove handlers from all loggers at teardown.
    This is to prevent pytest spitting out logging errors on teardown if the logging objects have been deinitialized
    (see https://github.com/pytest-dev/pytest/issues/5502#issuecomment-647157873).
    """
    loggers = [logging.getLogger()] + list(logging.Logger.manager.loggerDict.values())
    for logger in loggers:
        handlers = getattr(logger, 'handlers', [])
        for handler in handlers:
            logger.removeHandler(handler)


def _wait_for_app(app: Application, timeout: int = app_start_timeout):
    logging.info('Waiting for the app to start')
    start_time = time.time()
    http = None
    success = False

    while not http and time.time() - start_time < timeout:
        http = (app.backends or {}).get('http')
        time.sleep(1)

    assert http, f'HTTP backend not started after {timeout} seconds'

    while not success and time.time() - start_time < timeout:
        try:
            response = requests.get(f'http://localhost:{http.port}/')
            response.raise_for_status()
            success = True
        except Exception as e:
            logging.debug('App not ready yet: %s', e)
            time.sleep(1)

    assert success, f'App not ready after {timeout} seconds'


@pytest.fixture(scope='session', autouse=True)
def app():
    logging.info('Starting Platypush test service')

    Config.init(config_file)
    _app = Application(
        config_file=config_file,
        redis_queue='platypush-tests/bus',
        start_redis=True,
        redis_port=16379,
    )
    Thread(target=_app.run).start()
    _wait_for_app(_app)
    yield _app

    logging.info('Stopping Platypush test service')
    _app.stop()
    clear_loggers()
    db = (Config.get('main.db') or {}).get('engine', '')[len('sqlite:///') :]

    if db and os.path.isfile(db):
        logging.info('Removing temporary db file %s', db)
        os.unlink(db)


@pytest.fixture(scope='session')
def db_file():
    yield Config.get('main.db')['engine'][len('sqlite:///') :]


@pytest.fixture(scope='session')
def base_url():
    backends = Config.get_backends()
    assert 'http' in backends, 'Missing HTTP server configuration'
    url = f'http://localhost:{backends["http"]["port"]}'
    set_base_url(url)
    yield url
