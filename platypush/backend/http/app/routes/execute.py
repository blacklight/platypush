import json

from flask import Blueprint, abort, request, Response

from platypush.backend.http.app import template_folder
from platypush.backend.http.app.utils import authenticate, authentication_ok, \
    logger, send_message

from platypush.backend.http.utils import HttpUtils


execute = Blueprint('execute', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    execute,
]

@execute.route('/execute', methods=['POST'])
def execute():
    """ Endpoint to execute commands """
    if not authentication_ok(request): return authenticate()

    try:
        msg = json.loads(request.data.decode('utf-8'))
    except Exception as e:
        logger().error('Unable to parse JSON from request {}: {}'.format(
            request.data, str(e)))
        abort(400, str(e))

    logger().info('Received message on the HTTP backend: {}'.format(msg))

    try:
        response = send_message(msg)
        return Response(str(response or {}), mimetype='application/json')
    except Exception as e:
        logger().error('Error while running HTTP action: {}. Request: {}'.
                       format(str(e), msg))
        abort(500, str(e))


# vim:sw=4:ts=4:et:
