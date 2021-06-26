import json
import os

from platypush.utils import get_redis
from . import status_queue

environ_variables = [
    'PLAYER_EVENT',
    'TRACK_ID',
    'OLD_TRACK_ID',
    'DURATION_MS',
    'POSITION_MS',
    'VOLUME',
]


def on_librespot_event():
    get_redis().rpush(status_queue, json.dumps({
        var: os.environ[var]
        for var in environ_variables
        if var in os.environ
    }))


if __name__ == '__main__':
    on_librespot_event()
