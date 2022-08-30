import json

from flask import Blueprint, abort, request
from flask.wrappers import Response

from platypush.backend.http.app import template_folder
from platypush.backend.http.app.utils import logger, send_message
from platypush.config import Config
from platypush.event.hook import EventCondition
from platypush.message.event.http.hook import WebhookEvent


hook = Blueprint('hook', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    hook,
]


def matches_condition(event: WebhookEvent, hook):
    if isinstance(hook, dict):
        condition = hook.get('condition', {})
    else:
        condition = hook.condition

    condition = EventCondition.build(condition)
    return event.matches_condition(condition)


@hook.route(
    '/hook/<hook_name>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
)
def hook_route(hook_name):
    """Endpoint for custom webhooks"""

    event_args = {
        'hook': hook_name,
        'method': request.method,
        'args': dict(request.args or {}),
        'data': request.data.decode(),
        'headers': dict(request.headers or {}),
    }

    if event_args['data']:
        try:
            event_args['data'] = json.loads(event_args['data'])
        except Exception as e:
            logger().warning(
                'Not a valid JSON string: %s: %s', event_args['data'], str(e)
            )

    event = WebhookEvent(**event_args)
    matching_hooks = [
        hook
        for hook in Config.get_event_hooks().values()
        if matches_condition(event, hook)
    ]

    try:
        send_message(event)

        # If there are matching hooks, wait for their completion before returning
        if matching_hooks:
            return event.wait_response(timeout=60)

        return Response(
            json.dumps({'status': 'ok', **event_args}), mimetype='application/json'
        )
    except Exception as e:
        logger().exception(e)
        logger().error('Error while dispatching webhook event %s: %s', event, str(e))
        abort(500, str(e))


# vim:sw=4:ts=4:et:
