import logging

from ouimeaux.environment import Environment, UnknownDevice

from .. import SwitchPlugin

class SwitchWemoPlugin(SwitchPlugin):
    def _init(self):
        logging.basicConfig(level=logging.INFO)

        self.env = Environment()
        self.env.start()
        logging.info('Starting WeMo discovery')
        self.env.discover(seconds=3)

    def on(self, device):
        switch = self.env.get_switch(device)
        logging.info('Turning {} on'.format(device))
        switch.on()

    def off(self, device):
        switch = self.env.get_switch(device)
        logging.info('Turning {} off'.format(device))
        switch.off()

    def toggle(self, device):
        switch = self.env.get_switch(device)
        logging.info('Toggling {}'.format(device))
        switch.toggle()

    def status(self):
        return ['']

# vim:sw=4:ts=4:et:

