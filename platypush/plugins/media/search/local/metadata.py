import datetime
import json
import logging
import multiprocessing
import os
import subprocess
from concurrent.futures import ProcessPoolExecutor

from dateutil.parser import isoparse
import shutil

logger = logging.getLogger(__name__)


def get_file_metadata(path: str):
    """
    Retrieves the metadata of a media file using ffprobe.
    """
    logger.info('Retrieving metadata for %s', path)

    with subprocess.Popen(
        [
            'ffprobe',
            '-v',
            'quiet',
            '-print_format',
            'json',
            '-show_format',
            '-show_streams',
            path,
        ],
        stdout=subprocess.PIPE,
    ) as ffprobe:
        ret = json.loads(ffprobe.communicate()[0])

    video_stream = next(
        iter(
            [
                stream
                for stream in ret.get('streams', [])
                if stream.get('codec_type') == 'video'
            ]
        ),
        {},
    )

    creation_time = ret.get('format', {}).get('tags', {}).get('creation_time')
    if creation_time:
        try:
            creation_time = isoparse(creation_time)
        except ValueError:
            creation_time = None

    if not creation_time:
        creation_time = datetime.datetime.fromtimestamp(os.path.getctime(path))

    return {
        'duration': ret.get('format', {}).get('duration'),
        'width': video_stream.get('width'),
        'height': video_stream.get('height'),
        'created_at': creation_time,
    }


def get_metadata(*paths: str):
    """
    Retrieves the metadata of media files using ffprobe.
    """
    logger.info('Retrieving metadata for %d media files', len(paths))
    try:
        assert shutil.which(
            'ffprobe'
        ), 'ffprobe not found in PATH. Install ffmpeg to retrieve local media metadata.'

        # Run ffprobe in parallel
        with ProcessPoolExecutor(
            max_workers=multiprocessing.cpu_count() * 2
        ) as executor:
            futures = [executor.submit(get_file_metadata, path) for path in paths]
            results = [future.result() for future in futures]

        logger.info('Retrieved metadata for %d media files', len(results))
        return results
    except Exception as e:
        logger.error('Failed to retrieve media metadata: %s: %s', type(e).__name__, e)
        return [{} for _ in paths]
