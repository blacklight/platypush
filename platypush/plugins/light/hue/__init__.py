import logging
import time

from phue import Bridge
from platypush.message.response import Response

from .. import LightPlugin

class LightHuePlugin(LightPlugin):
    """ Philips Hue lights plugin """

    MAX_BRI = 255
    MAX_SAT = 255
    MAX_HUE = 65535

    def __init__(self, bridge, lights=None, groups=None):
        """
        Constructor
        Params:
            bridge -- Bridge address or hostname
            lights -- Lights to be controlled (default: all)
            groups -- Groups to be controlled (default: all)
        """

        super().__init__()

        self.bridge_address = bridge
        self.bridge = None
        logging.info('Initializing Hue lights plugin - bridge: "{}"'.
                     format(self.bridge_address))

        self.connect()
        self.lights = []; self.groups = []

        if lights:
            self.lights = lights
        elif groups:
            self.groups = groups
            self._expand_groups()
        else:
            self.lights = [l.name for l in self.bridge.lights]

        logging.info('Configured lights: "{}"'. format(self.lights))

    def _expand_groups(self):
        groups = [g for g in self.bridge.groups if g.name in self.groups]
        for g in groups:
            self.lights.extend([l.name for l in g.lights])

    def connect(self):
        # Lazy init
        if not self.bridge:
            self.bridge = Bridge(self.bridge_address)
            logging.info('Bridge connected')

            self.get_scenes()

            # uncomment these lines if you're running huectrl for
            # the first time and you need to pair it to the switch

            # self.bridge.connect()
            # self.bridge.get_api()
        else:
            logging.info('Bridge already connected')


    def get_scenes(self):
        scenes = [s.name for s in self.bridge.scenes]
        # TODO Expand it with custom scenes specified in config.yaml as in #14

    def _exec(self, attr, *args, **kwargs):
        try:
            self.connect()
        except Exception as e:
            # Reset bridge connection
            self.bridge = None
            raise e

        lights = []; groups = []
        if 'lights' in kwargs and kwargs['lights']:
            lights = kwargs['lights'].split(',') \
                if isinstance(lights, str) else kwargs['lights']
        elif 'groups' in kwargs and kwargs['lights']:
            groups = kwargs['groups'].split(',') \
                if isinstance(groups, str) else kwargs['groups']
        else:
            lights = self.lights
            groups = self.groups

        try:
            if attr == 'scene':
                self.bridge.run_scene(groups[0], kwargs['name'])
            elif groups:
                self.bridge.set_group(groups, attr, *args)
            elif lights:
                self.bridge.set_light(lights, attr, *args)
        except Exception as e:
            # Reset bridge connection
            self.bridge = None
            raise e

        return Response(output='ok')

    def on(self, lights=[], groups=[]):
        return self._exec('on', True, lights=lights, groups=groups)

    def off(self, lights=[], groups=[]):
        return self._exec('on', False, lights=lights, groups=groups)

    def bri(self, value, lights=[], groups=[]):
        return self._exec('bri', int(value) % (self.MAX_BRI+1),
                      lights=lights, groups=groups)

    def sat(self, value, lights=[], groups=[]):
        return self._exec('sat', int(value) % (self.MAX_SAT+1),
                      lights=lights, groups=groups)

    def hue(self, value, lights=[], groups=[]):
        return self._exec('hue', int(value) % (self.MAX_HUE+1),
                      lights=lights, groups=groups)

    def scene(self, name, lights=[], groups=[]):
        return self._exec('scene', name=name, lights=lights, groups=groups)


# vim:sw=4:ts=4:et:

