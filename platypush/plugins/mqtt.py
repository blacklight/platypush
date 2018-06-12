import json
import paho.mqtt.publish as publisher

from platypush.message import Message
from platypush.message.response import Response
from platypush.plugins import Plugin


class MqttPlugin(Plugin):
    def send_message(self, topic, msg, host, port=1883, *args, **kwargs):
        try: msg = json.dumps(msg)
        except: pass

        try: msg = Message.build(json.loads(msg))
        except: pass

        publisher.single(topic, str(msg), hostname=host, port=port)
        return Response(output={'state': 'ok'})


# vim:sw=4:ts=4:et:

