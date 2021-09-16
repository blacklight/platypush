import json

from flask import abort, request, Response, Blueprint, escape

from platypush.backend.http.app import template_folder
from platypush.common.spotify import SpotifyMixin
from platypush.utils import get_redis

spotify = Blueprint('spotify', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    spotify,
]


@spotify.route('/spotify/auth_callback', methods=['GET'])
def auth_callback():
    """
    This route is used as a callback URL for Spotify API authentication flows.
    """

    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')

    if not state:
        abort(400, 'No state parameters provided')

    msg = {'error': code} if error else {'code': code}
    get_redis().rpush(SpotifyMixin.get_spotify_queue_for_state(state), json.dumps(msg))

    if error:
        return Response(f'Authentication failed: {escape(error)}')

    return Response('Authentication successful. You can now close this window')


# vim:sw=4:ts=4:et:
