from platypush.config import Config

events_redis_topic = f'__platypush/{Config.get("device_id")}/events'  # type: ignore
