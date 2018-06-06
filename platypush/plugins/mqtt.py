import paho.mqtt.publish as publisher

from platypush.message.response import Response
from platypush.plugins import Plugin


class MqttPlugin(Plugin):
    def send_message(self, topic, msg, host, port=1883, *args, **kwargs):
        publisher.single(topic, str(msg), hostname=host, port=port)
        return Response(output={'state': 'ok'})


# vim:sw=4:ts=4:et:

