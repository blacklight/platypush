import os

from flask import Blueprint, render_template

from platypush.backend.http.app import template_folder, static_folder
from platypush.backend.http.app.utils import authenticate, get_websocket_port

from platypush.backend.http.utils import HttpUtils
from platypush.config import Config

panel = Blueprint('plugin', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    panel,
]


@panel.route('/plugin/<plugin>', methods=['GET'])
@authenticate()
def plugin_route(plugin):
    """ Route to the plugin pane template """
    js_folder = os.path.abspath(os.path.join(template_folder, '..', 'static', 'js'))
    style_folder = os.path.abspath(os.path.join(template_folder, '..', 'static', 'css', 'dist'))
    template_file = os.path.join(template_folder, 'plugins', plugin, 'index.html')
    script_file = os.path.join(js_folder, 'plugins', plugin, 'index.js')
    style_file = os.path.join(style_folder, 'webpanel', 'plugins', plugin+'.css')

    conf = Config.get(plugin) or {}
    if os.path.isfile(template_file):
        conf['_template_file'] = '/' + '/'.join(template_file.split(os.sep)[-3:])

    if os.path.isfile(script_file):
        conf['_script_file'] = '/'.join(script_file.split(os.sep)[-4:])

    if os.path.isfile(style_file):
        conf['_style_file'] = 'css/dist/' + style_file[len(style_folder)+1:]

    http_conf = Config.get('backend.http')
    return render_template('plugin.html',
                           plugin=plugin,
                           conf=conf,
                           template=conf.get('_template_file', {}),
                           script=conf.get('_script_file', {}),
                           style=conf.get('_style_file', {}),
                           utils=HttpUtils,
                           token=Config.get('token'),
                           websocket_port=get_websocket_port(),
                           template_folder=template_folder,
                           static_folder=static_folder,
                           has_ssl=http_conf.get('ssl_cert') is not None)


# vim:sw=4:ts=4:et:
