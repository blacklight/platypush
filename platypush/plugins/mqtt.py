import json
import paho.mqtt.publish as publisher

from platypush.message import Message
from platypush.plugins import Plugin, action


class MqttPlugin(Plugin):
    """
    This plugin allows you to send custom message to a message queue compatible
    with the MQTT protocol, see http://mqtt.org/
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @action
    def send_message(self, topic, msg, host, port=1883, *args, **kwargs):
        """
        Sends a message to a topic/channel.

        :param topic: Topic/channel where the message will be delivered
        :type topic: str

        :param msg: Message to be sent. It can be a list, a dict, or a Message object

        :param host: MQTT broker hostname/IP
        :type host: str

        :param port: MQTT broker port (default: 1883)
        :type port: int
        """

        try: msg = json.dumps(msg)
        except: pass

        try: msg = Message.build(json.loads(msg))
        except: pass

        publisher.single(topic, str(msg), hostname=host, port=port)


# vim:sw=4:ts=4:et:

