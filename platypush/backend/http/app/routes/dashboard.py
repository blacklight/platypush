from flask import Blueprint, request, render_template

from platypush.backend.http.app import template_folder
from platypush.backend.http.app.utils import authenticate, get_websocket_port
from platypush.backend.http.utils import HttpUtils

dashboard = Blueprint('dashboard', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    dashboard,
]


@dashboard.route('/dashboard/<name>', methods=['GET'])
@authenticate()
def render_dashboard(*_, **__):
    """ Route for the dashboard """
    return render_template('index.html',
                           utils=HttpUtils,
                           websocket_port=get_websocket_port())


# vim:sw=4:ts=4:et:
