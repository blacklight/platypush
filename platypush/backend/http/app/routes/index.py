import os

from flask import Blueprint, request, render_template

from platypush.backend.http.app import template_folder, static_folder
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
    if not authentication_ok(request):
        return authenticate()

    configured_plugins = Config.get_plugins()
    enabled_templates = {}
    enabled_scripts = {}
    enabled_styles = {}

    js_folder = os.path.abspath(
        os.path.join(template_folder, '..', 'static', 'js'))
    style_folder = os.path.abspath(
        os.path.join(template_folder, '..', 'static', 'css', 'dist'))

    for plugin, conf in configured_plugins.items():
        template_file = os.path.join(
            template_folder, 'plugins', plugin, 'index.html')

        script_file = os.path.join(js_folder, 'plugins', plugin, 'index.js')
        style_file = os.path.join(style_folder, 'webpanel', 'plugins', plugin+'.css')

        if os.path.isfile(template_file):
            conf['_template_file'] = '/' + '/'.join(template_file.split(os.sep)[-3:])
            enabled_templates[plugin] = conf

        if os.path.isfile(script_file):
            conf['_script_file'] = '/'.join(script_file.split(os.sep)[-4:])
            enabled_scripts[plugin] = conf

        if os.path.isfile(style_file):
            conf['_style_file'] = 'css/dist/' + style_file[len(style_folder)+1:]
            enabled_styles[plugin] = conf

    http_conf = Config.get('backend.http')
    return render_template('index.html', templates=enabled_templates,
                           scripts=enabled_scripts, styles=enabled_styles,
                           utils=HttpUtils, token=Config.get('token'),
                           websocket_port=get_websocket_port(),
                           template_folder=template_folder, static_folder=static_folder,
                           plugins=Config.get_plugins(), backends=Config.get_backends(),
                           has_ssl=http_conf.get('ssl_cert') is not None)


# vim:sw=4:ts=4:et:
