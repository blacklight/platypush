import json

import paho.mqtt.client as mqtt
import paho.mqtt.publish as publisher

from platypush.backend import Backend
from platypush.message import Message


class MqttBackend(Backend):
    """
    Backend that reads messages from a configured MQTT topic (default:
    ``platypush_bus_mq/<device_id>``) and posts them to the application bus.

    Requires:

        * **paho-mqtt** (``pip install paho-mqtt``)
    """

    def __init__(self, host, port=1883, topic='platypush_bus_mq', *args, **kwargs):
        """
        :param host: MQTT broker host
        :type host: str

        :param port: MQTT broker port (default: 1883)
        :type port: int

        :param topic: Topic to read messages from (default: ``platypush_bus_mq/<device_id>``)
        :type topic: str
        """

        super().__init__(*args, **kwargs)

        self.host = host
        self.port = port
        self.topic = '{}/{}'.format(topic, self.device_id)


    def send_message(self, msg):
        try:
            msg = Message.build(json.loads(msg))
        except:
            pass

        publisher.single(self.topic, str(msg), hostname=self.host, port=self.port)


    def run(self):
        def on_connect(client, userdata, flags, rc):
            client.subscribe(self.topic)

        def on_message(client, userdata, msg):
            msg = msg.payload.decode('utf-8')
            try: msg = Message.build(json.loads(msg))
            except: pass

            self.logger.info('Received message on the MQTT backend: {}'.format(msg))
            self.bus.post(msg)

        super().run()
        client = mqtt.Client()
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(self.host, self.port, 60)
        self.logger.info('Initialized MQTT backend on host {}:{}, topic {}'.
                     format(self.host, self.port, self.topic))

        client.loop_forever()


# vim:sw=4:ts=4:et:

