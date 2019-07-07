from flask import Blueprint, request, render_template

from platypush.backend.http.app import template_folder, static_folder
from platypush.backend.http.app.utils import authenticate, authentication_ok, \
    get_websocket_port

from platypush.backend.http.utils import HttpUtils
from platypush.config import Config

dashboard = Blueprint('dashboard', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    dashboard,
]


@dashboard.route('/dashboard', methods=['GET'])
def dashboard():
    """ Route for the fullscreen dashboard """
    if not authentication_ok(request):
        return authenticate()

    http_conf = Config.get('backend.http')
    dashboard_conf = http_conf.get('dashboard', {})

    return render_template('dashboard.html', config=dashboard_conf,
                           utils=HttpUtils, token=Config.get('token'),
                           static_folder=static_folder, template_folder=template_folder,
                           websocket_port=get_websocket_port(),
                           has_ssl=http_conf.get('ssl_cert') is not None)


# vim:sw=4:ts=4:et:
