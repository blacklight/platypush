import logging

from ouimeaux.environment import Environment, UnknownDevice

from .. import SwitchPlugin

class SwitchWemoPlugin(SwitchPlugin):
    _requires = [
        'ouimeaux'
    ]

    def _init(self):
        logging.basicConfig(level=logging.INFO)

        self.env = Environment()
        self.env.start()
        logging.info('Starting WeMo discovery')
        self.env.discover(seconds=3)

    def on(self, args):
        switch = self.env.get_switch(args['device'])
        logging.info('Turning {} on'.format(args['device']))
        switch.on()

    def off(self, args):
        switch = self.env.get_switch(args['device'])
        logging.info('Turning {} off'.format(args['device']))
        switch.off()

    def toggle(self, args):
        switch = self.env.get_switch(args['device'])
        logging.info('Toggling {}'.format(args['device']))
        switch.toggle()

    def status(self):
        return ['']

# vim:sw=4:ts=4:et:

