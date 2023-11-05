from typing import Dict

from platypush.backend.http.media.handlers import MediaHandler


# Size for the bytes chunk sent over the media streaming infra
STREAMING_CHUNK_SIZE = 4096

# Maximum range size to be sent through the media streamer if Range header
# is not set
STREAMING_BLOCK_SIZE = 3145728

# Name of the Redis variable used to store the media map across several
# Web processes
MEDIA_MAP_VAR = 'platypush__stream_media_map'

MediaMap = Dict[str, MediaHandler]
