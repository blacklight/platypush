import json

from flask import Blueprint, abort, request, Response

from platypush.backend.http.app import template_folder
from platypush.backend.http.app.utils import authenticate, logger, send_message

execute = Blueprint('execute', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    execute,
]


@execute.route('/execute', methods=['POST'])
@authenticate(skip_auth_methods=['session'])
def execute():
    """ Endpoint to execute commands """
    try:
        msg = json.loads(request.data.decode('utf-8'))
    except Exception as e:
        logger().error('Unable to parse JSON from request {}: {}'.format(request.data, str(e)))
        return abort(400, str(e))

    logger().info('Received message on the HTTP backend: {}'.format(msg))

    try:
        response = send_message(msg)
        return Response(str(response or {}), mimetype='application/json')
    except Exception as e:
        logger().error('Error while running HTTP action: {}. Request: {}'.format(str(e), msg))
        return abort(500, str(e))


# vim:sw=4:ts=4:et:
