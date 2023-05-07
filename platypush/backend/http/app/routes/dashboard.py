from flask import Blueprint, render_template

from platypush.backend.http.app import template_folder
from platypush.backend.http.app.utils import authenticate
from platypush.backend.http.utils import HttpUtils

dashboard = Blueprint('dashboard', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    dashboard,
]


# noinspection PyUnusedLocal
@dashboard.route('/dashboard/<name>', methods=['GET'])
@authenticate()
def render_dashboard(name):
    """Route for the dashboard"""
    return render_template(
        'index.html',
        utils=HttpUtils,
    )


# vim:sw=4:ts=4:et:
