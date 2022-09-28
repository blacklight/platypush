import json

from flask import Blueprint, abort, request, make_response

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
        if_ = hook['if'].copy()
        if_['type'] = '.'.join([event.__module__, event.__class__.__qualname__])

        condition = EventCondition.build(if_)
    else:
        condition = hook.condition

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
        rs = default_rs = make_response(json.dumps({'status': 'ok', **event_args}))
        headers = {}
        status_code = 200

        # If there are matching hooks, wait for their completion before returning
        if matching_hooks:
            rs = event.wait_response(timeout=60)
            try:
                rs = json.loads(rs.decode())  # type: ignore
            except Exception:
                pass

            if isinstance(rs, dict) and '___data___' in rs:
                # data + http_code + custom_headers return format
                headers = rs.get('___headers___', {})
                status_code = rs.get('___code___', status_code)
                rs = rs['___data___']

            if rs is None:
                rs = default_rs
                headers = {'Content-Type': 'application/json'}

            rs = make_response(rs)
        else:
            headers = {'Content-Type': 'application/json'}

        rs.status_code = status_code
        rs.headers.update(headers)
        return rs
    except Exception as e:
        logger().exception(e)
        logger().error('Error while dispatching webhook event %s: %s', event, str(e))
        abort(500, str(e))


# vim:sw=4:ts=4:et:
