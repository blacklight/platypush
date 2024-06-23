import os
import re
from typing import Generator

from flask import Blueprint, abort, request
from flask.wrappers import Response

from platypush.backend.http.app import template_folder
from platypush.backend.http.app.utils import authenticate, logger
from platypush.utils import get_mime_type

file = Blueprint('file', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    file,
]


@file.route('/file', methods=['GET', 'HEAD'])
@authenticate()
def get_file_route():
    """
    Endpoint to read the content of a file on the server.
    """

    def read_file(path: str) -> Generator[bytes, None, None]:
        with open(path, 'rb') as f:
            yield from iter(lambda: f.read(4096), b'')

    path = os.sep + os.path.join(
        *[
            token
            for token in re.sub(
                r'^\.\./',
                '',
                re.sub(
                    r'^\./',
                    '',
                    request.args.get('path', '').lstrip(os.sep).lstrip(' ') or '',
                ),
            ).split(os.sep)
            if token
        ]
    )

    logger().debug('Received file read request for %r', request.path)

    if not os.path.isfile(path):
        logger().warning('File not found: %r', path)
        abort(404, 'File not found')

    try:
        headers = {
            'Content-Length': str(os.path.getsize(path)),
            'Content-Type': (get_mime_type(path) or 'application/octet-stream'),
        }

        if request.method == 'HEAD':
            return Response(status=200, headers=headers)

        return read_file(path), 200, headers
    except PermissionError:
        logger().warning('Permission denied to read file %r', path)
        abort(403, 'Permission denied')


# vim:sw=4:ts=4:et:
