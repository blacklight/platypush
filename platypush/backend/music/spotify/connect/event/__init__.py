from platypush.bus.redis import RedisBus

status_queue = 'platypush/music/spotify/connect/status'


def get_redis() -> RedisBus:
    return RedisBus(redis_queue=status_queue)
