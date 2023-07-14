import json

from flask import Blueprint, abort, request
from flask.wrappers import Response

from platypush.backend.http.app import template_folder
from platypush.backend.http.app.utils import authenticate, logger, send_message

execute = Blueprint('execute', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    execute,
]


@execute.route('/execute', methods=['POST'])
@authenticate(json=True)
def execute_route():
    """Endpoint to execute commands"""
    try:
        msg = json.loads(request.data.decode('utf-8'))
    except Exception as e:
        logger().error('Unable to parse JSON from request %s: %s', request.data, e)
        abort(400, str(e))

    logger().debug(
        'Received message on the HTTP backend from %s: %s', request.remote_addr, msg
    )

    try:
        response = send_message(msg)
        return Response(str(response or {}), mimetype='application/json')
    except Exception as e:
        logger().error('Error while running HTTP action: %s. Request: %s', e, msg)
        abort(500, str(e))


# vim:sw=4:ts=4:et:
