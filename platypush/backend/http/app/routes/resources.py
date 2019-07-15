import os
import re

from flask import Blueprint, abort, send_from_directory

from platypush.config import Config
from platypush.backend.http.app import template_folder, static_folder


img_folder = os.path.join(static_folder, 'resources', 'img')
resources = Blueprint('resources', __name__, template_folder=template_folder)
favicon = Blueprint('favicon', __name__, template_folder=template_folder)
img = Blueprint('img', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    resources,
    favicon,
    img,
]


@resources.route('/resources/<path:path>', methods=['GET'])
def resources_path(path):
    """ Custom static resources """
    path_tokens = path.split('/')
    filename = path_tokens.pop(-1)
    http_conf = Config.get('backend.http')
    resource_dirs = http_conf.get('resource_dirs', {})

    while path_tokens:
        if '/'.join(path_tokens) in resource_dirs:
            break
        path_tokens.pop()

    if not path_tokens:
        # Requested resource not found in the allowed resource_dirs
        abort(404)

    base_path = '/'.join(path_tokens)
    real_base_path = os.path.abspath(os.path.expanduser(resource_dirs[base_path]))
    real_path = real_base_path

    file_path = [s for s in re.sub(r'^{}(.*)$'.format(base_path), '\\1', path)
                 .split('/') if s]

    for p in file_path[:-1]:
        real_path += os.sep + p
        file_path.pop(0)

    file_path = file_path.pop(0)
    if not real_path.startswith(real_base_path):
        # Directory climbing attempt
        abort(404)

    return send_from_directory(real_path, file_path)


@favicon.route('/favicon.ico', methods=['GET'])
def favicon():
    """ favicon.ico icon """
    return send_from_directory(img_folder, 'favicon.ico')

@img.route('/img/<path:path>', methods=['GET'])
def imgpath(path):
    """ Default static images """
    return send_from_directory(img_folder, path)


# vim:sw=4:ts=4:et:
