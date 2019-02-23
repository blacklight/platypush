import json

from flask import abort, jsonify, request, Blueprint

from platypush.backend.http.app import template_folder
from platypush.backend.http.app.utils import logger, get_remote_base_url
from platypush.backend.http.app.routes.plugins.media import media_map, \
    stream_media, register_media, unregister_media

media = Blueprint('media', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    media,
]

@media.route('/media', methods=['GET'])
def get_media():
    """
    This route can be used to get the list of registered streams
    """
    return jsonify([dict(media) for media in media_map.values()])


@media.route('/media', methods=['PUT'])
def add_media():
    """
    This route can be used by the `media` plugin to add streaming content over HTTP
    """

    args = {}
    try:
        args = json.loads(request.data.decode('utf-8'))
    except:
        abort(400, 'Invalid JSON request')

    source = args.get('source')
    if not source:
        abort(400, 'The request does not contain any source')

    subtitles = args.get('subtitles')
    try:
        media_hndl = register_media(source, subtitles)
        ret = dict(media_hndl)
        if media_hndl.subtitles:
            ret['subtitles_url'] = get_remote_base_url() + \
                '/media/subtitles/' + media_hndl.media_id + '.vtt'
        return jsonify(ret)
    except FileNotFoundError as e:
        abort(404, str(e))
    except AttributeError as e:
        abort(400, str(e))
    except Exception as e:
        logger().exception(e)
        abort(500, str(e))


@media.route('/media/<media_id>', methods=['GET', 'DELETE'])
def stream_or_delete_media(media_id):
    """
    This route can be used to stream active media points or unregister
    a mounted media stream
    """

    # Remove the extension
    media_id = '.'.join(media_id.split('.')[:-1])

    try:
        if request.method == 'GET':
            if media_id is None:
                return jsonify([dict(media) for media in media_map.values()])
            else:
                return stream_media(media_id, request)
        else:
            media_info = unregister_media(media_id)
            return jsonify(media_info)
    except (AttributeError, FileNotFoundError) as e:
        abort(404, str(e))
    except KeyError as e:
        abort(400, str(e))
    except Exception as e:
        logger().exception(e)
        abort(500, str(e))


# vim:sw=4:ts=4:et:
