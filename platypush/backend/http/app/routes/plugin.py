from flask import Blueprint, render_template

from platypush.backend.http.app import template_folder
from platypush.backend.http.app.utils import authenticate

from platypush.backend.http.utils import HttpUtils

panel = Blueprint('plugin', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    panel,
]


@panel.route('/plugin/<plugin>', methods=['GET'])
@authenticate()
def plugin_route(plugin):
    """ Route to the plugin panel template """
    return render_template('index.html', plugin=plugin, utils=HttpUtils)


# vim:sw=4:ts=4:et:
