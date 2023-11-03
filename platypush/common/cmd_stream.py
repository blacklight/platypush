from platypush.config import Config


redis_topic = f'_platypush/{Config.get("device_id")}/shell/cmd'
