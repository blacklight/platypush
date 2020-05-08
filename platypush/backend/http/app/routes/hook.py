import json

from flask import Blueprint, abort, request, Response

from platypush.backend.http.app import template_folder
from platypush.backend.http.app.utils import authenticate, logger, send_message

from platypush.message.event.http.hook import WebhookEvent


hook = Blueprint('hook', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    hook,
]


@hook.route('/hook/<hook_name>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
@authenticate(skip_auth_methods=['session'])
def _hook(hook_name):
    """ Endpoint for custom webhooks """

    event_args = {
        'hook': hook_name,
        'method': request.method,
        'args': dict(request.args or {}),
        'data': request.data.decode(),
    }

    if event_args['data']:
        # noinspection PyBroadException
        try:
            event_args['data'] = json.loads(event_args['data'])
        except:
            pass

    event = WebhookEvent(**event_args)

    try:
        send_message(event)
        return Response(json.dumps({'status': 'ok', **event_args}), mimetype='application/json')
    except Exception as e:
        logger().exception(e)
        logger().error('Error while dispatching webhook event {}: {}'.format(event, str(e)))
        abort(500, str(e))


# vim:sw=4:ts=4:et:
