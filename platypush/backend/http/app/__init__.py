import logging
import os

from flask import Flask

from platypush import Config
from platypush.backend.http.app.utils import get_routes


def initialize_logger():
    logger = logging.getLogger('werkzeug')
    try:
        log_conf = Config.get('logging')
        if 'level' in log_conf:
            logger.setLevel(log_conf['level'])
    except Exception as e:
        logger.warning('Could not read logging level')
        logger.exception(e)


## Webapp initialization

initialize_logger()

base_folder = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..'))

template_folder = os.path.join(base_folder, 'webapp/dist')
static_folder = os.path.join(base_folder, 'webapp/dist/static')

application = Flask('platypush',
                    template_folder=template_folder,
                    static_folder=static_folder)

for route in get_routes():
    application.register_blueprint(route)


# vim:sw=4:ts=4:et:
