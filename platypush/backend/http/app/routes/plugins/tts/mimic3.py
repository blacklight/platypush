import requests
from urllib.parse import urljoin

from flask import abort, request, Blueprint

from platypush.backend.http.app import template_folder

mimic3 = Blueprint('mimic3', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    mimic3,
]


@mimic3.route('/tts/mimic3/say', methods=['GET'])
def proxy_tts_request():
    """
    This route is used to proxy the POST request to the Mimic3 TTS server
    through a GET, so it can be easily processed as a URL through a media
    plugin.
    """
    required_args = {
        'text',
        'server_url',
        'voice',
    }

    missing_args = required_args.difference(set(request.args.keys()))
    if missing_args:
        abort(400, f'Missing parameters: {missing_args}')

    args = {arg: request.args[arg] for arg in required_args}

    rs = requests.post(
        urljoin(args['server_url'], '/api/tts'),
        data=args['text'],
        params={
            'voice': args['voice'],
        },
    )

    return rs.content


# vim:sw=4:ts=4:et:
