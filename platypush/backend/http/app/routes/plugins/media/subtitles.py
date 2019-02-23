import os

from flask import abort, jsonify, request, send_from_directory, Blueprint

from platypush.backend.http.app import template_folder
from platypush.backend.http.app.routes.plugins.media import media_map, \
    remove_subtitles, add_subtitles

subtitles = Blueprint('subtitles', __name__, template_folder=template_folder)

# Declare routes list
__routes__ = [
    subtitles,
]

@subtitles.route('/media/subtitles/<media_id>.vtt', methods=['GET', 'POST', 'DELETE'])
def handle_subtitles(media_id):
    """
    This route can be used to download and/or expose subtitle files
    associated to a media file
    """

    if request.method == 'GET':
        media_hndl = media_map.get(media_id)
        if not media_hndl:
            abort(404, 'No such media')

        if not media_hndl.subtitles:
            abort(404, 'The media has no subtitles attached')

        return send_from_directory(
            os.path.dirname(media_hndl.subtitles),
            os.path.basename(media_hndl.subtitles),
            mimetype='text/vtt')

    try:
        if request.method == 'DELETE':
            return jsonify(remove_subtitles(media_id))
        else:
            return jsonify(add_subtitles(media_id, request))
    except FileNotFoundError as e:
        abort(404, str(e))
    except AttributeError as e:
        abort(400, str(e))
    except NotImplementedError as e:
        abort(422, str(e))
    except Exception as e:
        abort(500, str(e))


# vim:sw=4:ts=4:et:
