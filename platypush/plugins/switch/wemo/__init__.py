import logging
import json

from ouimeaux.environment import Environment, UnknownDevice
from platypush.message.response import Response

from .. import SwitchPlugin

class SwitchWemoPlugin(SwitchPlugin):
    def __init__(self, discovery_seconds=3):
        super().__init__()

        self.discovery_seconds=discovery_seconds
        self.env = Environment()
        self.env.start()
        self.refresh_devices()

    def refresh_devices(self):
        logging.info('Starting WeMo discovery')
        self.env.discover(seconds=self.discovery_seconds)
        self.devices = self.env.devices

    def _exec(self, method, device, *args, **kwargs):
        if device not in self.devices:
            self.refresh_devices()

        if device not in self.devices:
            raise RuntimeError('Device {} not found'.format(device))

        logging.info('{} -> {}'.format(device, method))
        dev = self.devices[device]
        getattr(dev, method)(*args, **kwargs)

        resp = {'device': device, 'state': dev.get_state()}
        return Response(output=json.dumps(resp))

    def on(self, device):
        return self._exec('on', device)

    def off(self, device):
        return self._exec('off', device)

    def toggle(self, device):
        return self._exec('toggle', device)


# vim:sw=4:ts=4:et:

