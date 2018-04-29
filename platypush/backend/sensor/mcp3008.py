import logging
import time

from platypush.backend import Backend
from platypush.context import get_plugin
from platypush.message.event.sensor import SensorDataChangeEvent
from platypush.plugins.gpio.sensor.mcp3008 import GpioSensorMcp3008Plugin


class SensorMcp3008Backend(Backend):
    last_measurement = {}

    def __init__(self, poll_seconds, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.poll_seconds = poll_seconds
        logging.info('Initialized MCP3008 analog sensors backend')


    def send_message(self, msg):
        pass


    def run(self):
        super().run()
        plugin = get_plugin('gpio.sensor.mcp3008')

        while not self.should_stop():
            try:
                measurement = plugin.get_measurement().output
            except:
                plugin = get_plugin('gpio.sensor.mcp3008', reload=True)

            new_measurement = {}
            for key in measurement.keys():
                if key not in self.last_measurement \
                        or measurement[key] != self.last_measurement[key]:
                    new_measurement[key] = measurement[key]

            if new_measurement:
                self.bus.post(SensorDataChangeEvent(sensors=new_measurement))

            self.last_measurement = measurement
            time.sleep(self.poll_seconds)


# vim:sw=4:ts=4:et:

