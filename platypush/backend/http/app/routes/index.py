import os

from flask import Blueprint, request, render_template

from platypush.backend.http.app import template_folder
from platypush.backend.http.app.utils import authenticate, authentication_ok, \
    get_websocket_port

from platypush.backend.http.utils import HttpUtils
from platypush.config import Config


index = Blueprint('index', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    index,
]

@index.route('/')
def index():
    """ Route to the main web panel """
    if not authentication_ok(request): return authenticate()

    # These plugins have their own template file but won't be shown as a tab in
    # the web panel. This is usually the case for plugins that only include JS
    # code but no template content.
    _hidden_plugins = {
        'assistant.google'
    }

    configured_plugins = Config.get_plugins()
    enabled_plugins = {}
    hidden_plugins = {}

    for plugin, conf in configured_plugins.items():
        template_file = os.path.join('plugins', plugin + '.html')
        if os.path.isfile(os.path.join(template_folder, template_file)):
            if plugin in _hidden_plugins:
                hidden_plugins[plugin] = conf
            else:
                enabled_plugins[plugin] = conf

    http_conf = Config.get('backend.http')
    return render_template('index.html', plugins=enabled_plugins,
                            hidden_plugins=hidden_plugins, utils=HttpUtils,
                            token=Config.get('token'),
                            websocket_port=get_websocket_port(),
                            has_ssl=http_conf.get('ssl_cert') is not None)


# vim:sw=4:ts=4:et:
