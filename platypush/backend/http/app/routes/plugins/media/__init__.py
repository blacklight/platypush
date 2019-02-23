import hashlib
import json
import threading

from flask import Response, render_template

from platypush.backend.http.app.utils import get_remote_base_url, logger, \
    send_message

from platypush.backend.http.media.handlers import MediaHandler

media_map = {}
media_map_lock = threading.RLock()

# Size for the bytes chunk sent over the media streaming infra
STREAMING_CHUNK_SIZE = 4096

# Maximum range size to be sent through the media streamer if Range header
# is not set
STREAMING_BLOCK_SIZE = 3145728


def get_media_url(media_id):
    return '{url}/media/{media_id}'.format(
        url=get_remote_base_url(), media_id=media_id)

def get_media_id(source):
    return hashlib.sha1(source.encode()).hexdigest()

def register_media(source, subtitles=None):
    global media_map, media_map_lock

    media_id = get_media_id(source)
    media_url = get_media_url(media_id)

    with media_map_lock:
        if media_id in media_map:
            return media_map[media_id]

    subfile = None
    if subtitles:
        req = {
            'type': 'request',
            'action': 'media.subtitles.download',
            'args': {
                'link': subtitles,
                'convert_to_vtt': True,
            }
        }

        try:
            subfile = (send_message(req).output or {}).get('filename')
        except Exception as e:
            logger().warning('Unable to load subtitle {}: {}'
                             .format(subtitles, str(e)))

    with media_map_lock:
        media_hndl = MediaHandler.build(source, url=media_url, subtitles=subfile)
        media_map[media_id] = media_hndl
        media_hndl.media_id = media_id

    logger().info('Streaming "{}" on {}'.format(source, media_url))
    return media_hndl


def unregister_media(source):
    global media_map, media_map_lock

    if source is None:
        raise KeyError('No media_id specified')

    media_id = get_media_id(source)
    media_info = {}

    with media_map_lock:
        if media_id not in media_map:
            raise FileNotFoundError('{} is not a registered media_id'.
                                    format(source))
        media_info = media_map.pop(media_id)

    logger().info('Unregistered {} from {}'.format(source, media_info.get('url')))
    return media_info


def stream_media(media_id, req):
    global STREAMING_BLOCK_SIZE, STREAMING_CHUNK_SIZE

    media_hndl = media_map.get(media_id)
    if not media_hndl:
        raise FileNotFoundError('{} is not a registered media_id'.format(media_id))

    from_bytes = None
    to_bytes = None
    range_hdr = req.headers.get('range')
    content_length = media_hndl.content_length
    status_code = 200

    headers = {
        'Accept-Ranges': 'bytes',
        'Content-Type': media_hndl.mime_type,
    }

    if 'download' in req.args:
        headers['Content-Disposition'] = 'attachment' + \
            ('; filename="{}"'.format(media_hndl.filename) if
             media_hndl.filename else '')

    if range_hdr:
        headers['Accept-Ranges'] = 'bytes'
        from_bytes, to_bytes = range_hdr.replace('bytes=', '').split('-')
        from_bytes = int(from_bytes)

        if not to_bytes:
            to_bytes = content_length-1
            content_length -= from_bytes
        else:
            to_bytes = int(to_bytes)
            content_length = to_bytes - from_bytes

        status_code = 206
        headers['Content-Range'] = 'bytes {start}-{end}/{size}'.format(
            start=from_bytes, end=to_bytes,
            size=media_hndl.content_length)
    else:
        from_bytes = 0
        to_bytes = STREAMING_BLOCK_SIZE

    headers['Content-Length'] = content_length

    if 'webplayer' in req.args:
        return render_template('webplayer.html',
                                media_url=media_hndl.url.replace(
                                    get_remote_base_url(), ''),
                                media_type=media_hndl.mime_type,
                                subtitles_url='/media/subtitles/{}.vtt'.
                                format(media_id) if media_hndl.subtitles
                                else None)
    else:
        return Response(media_hndl.get_data(
            from_bytes=from_bytes, to_bytes=to_bytes,
            chunk_size=STREAMING_CHUNK_SIZE),
            status_code, headers=headers, mimetype=headers['Content-Type'],
            direct_passthrough=True)


def add_subtitles(media_id, req):
    """
    This route can be used to download and/or expose subtitles files
    associated to a media file
    """

    media_hndl = media_map.get(media_id)
    if not media_hndl:
        raise FileNotFoundError('{} is not a registered media_id'.format(media_id))

    subfile = None
    if req.data:
        subfile = json.loads(req.data.decode('utf-8')).get('filename')
        if not subfile:
            raise AttributeError('No filename specified in the request')

    if not subfile:
        if not media_hndl.path:
            raise NotImplementedError(
                'Subtitles are currently only supported for local media files')

        req = {
            'type': 'request',
            'action': 'media.subtitles.get_subtitles',
            'args': {
                'resource': media_hndl.path,
            }
        }

        try:
            subtitles = send_message(req).output or []
        except Exception as e:
            raise RuntimeError('Could not get subtitles: {}'.format(str(e)))

        if not subtitles:
            raise FileNotFoundError('No subtitles found for resource {}'.
                                    format(media_hndl.path))

        req = {
            'type': 'request',
            'action': 'media.subtitles.download',
            'args': {
                'link': subtitles[0].get('SubDownloadLink'),
                'media_resource': media_hndl.path,
                'convert_to_vtt': True,
            }
        }

        subfile = (send_message(req).output or {}).get('filename')

    media_hndl.set_subtitles(subfile)
    return {
        'filename': subfile,
        'url': get_remote_base_url() + '/media/subtitles/' + media_id + '.vtt',
    }

def remove_subtitles(media_id):
    media_hndl = media_map.get(media_id)
    if not media_hndl:
        raise FileNotFoundError('{} is not a registered media_id'.
                                format(media_id))

    if not media_hndl.subtitles:
        raise FileNotFoundError('{} has no subtitles attached'.
                                format(media_id))

    media_hndl.remove_subtitles()
    return {}



# vim:sw=4:ts=4:et:
