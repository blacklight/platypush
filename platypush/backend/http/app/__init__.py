import os

from flask import Flask

from platypush.backend.http.app.utils import get_routes


## Webapp initialization

base_folder = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..'))

template_folder = os.path.join(base_folder, 'templates')
static_folder = os.path.join(base_folder, 'static')

application = Flask('platypush', template_folder=template_folder,
                    static_folder=static_folder)

for route in get_routes():
    application.register_blueprint(route)


# vim:sw=4:ts=4:et:
