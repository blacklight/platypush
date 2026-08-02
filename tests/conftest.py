import logging
import os
import time
from threading import Thread

import pytest
import requests

from platypush import Application, Config

from .utils import config_file, set_base_url

app_start_timeout = 15

# Initialize the configuration singleton with the test configuration as soon
# as this module is imported. pytest imports conftest.py before collecting the
# test modules, some of which import Platypush modules that may lazily
# initialize the Config singleton - and they would otherwise pick up the
# default (user/system) configuration file instead of the test one.
Config.init(config_file)


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

    if not (http):
        raise AssertionError(f'HTTP backend not started after {timeout} seconds')

    while not success and time.time() - start_time < timeout:
        try:
            response = requests.get(
                f'http://localhost:{http.port}/', timeout=1, allow_redirects=False
            )
            response.raise_for_status()
            success = True
        except Exception as e:
            logging.info('App not ready yet: %s', e)
            time.sleep(1)

    if not (success):
        raise AssertionError(f'App not ready after {timeout} seconds')


def _clear_db_file():
    db = (Config.get('main.db') or {}).get('engine', '')[len('sqlite:///') :]

    if db and os.path.isfile(db):
        logging.info('Removing temporary db file %s', db)
        os.unlink(db)


@pytest.fixture(scope='session', autouse=True)
def app():
    logging.info('Starting Platypush test service')

    Config.init(config_file)
    # Remove any stale db file from a previous test run that may have crashed
    # before its teardown could clean it up.
    _clear_db_file()

    _app = Application(
        config_file=config_file,
        redis_queue='platypush-tests/bus',
        start_redis=True,
        redis_port=16379,
    )
    Thread(target=_app.run).start()

    try:
        _wait_for_app(_app)
    except Exception:
        # If the app failed to start, make sure that whatever was brought up
        # (app threads, Redis) is stopped, or the pytest process will hang
        # around forever and hold ports busy for the next runs.
        logging.exception('The application failed to start, stopping it')
        _app.stop()
        raise

    yield _app

    logging.info('Stopping Platypush test service')
    _app.stop()
    clear_loggers()
    _clear_db_file()


@pytest.fixture(scope='session')
def db_file():
    yield Config.get('main.db')['engine'][len('sqlite:///') :]


@pytest.fixture(scope='session')
def base_url():
    backends = Config.get_backends()
    if not ('http' in backends):
        raise AssertionError('Missing HTTP server configuration')
    url = f'http://localhost:{backends["http"]["port"]}'
    set_base_url(url)
    yield url
