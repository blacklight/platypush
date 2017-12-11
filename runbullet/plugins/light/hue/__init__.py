import logging

from phue import Bridge

from .. import LightPlugin

class LightHuePlugin(LightPlugin):
    """ Python dependencies """
    _requires = [
        'phue'
    ]

    MAX_BRI = 255
    MAX_SAT = 255
    MAX_HUE = 65535

    def _init(self):
        self.bridge_address = self.config['bridge']
        self.bridge = None
        logging.info('Initializing Hue lights plugin - bridge: "{}"'.
                     format(self.bridge_address))

        self.connect()
        self.lights = []; self.groups = []

        if 'lights' in self.config:
            self.lights = self.config['lights']
        elif 'groups' in self.config:
            self.groups = self.config['groups']
            self._expand_groups(self.groups)
        else:
            self.lights = [l.name for l in self.bridge.lights]

        logging.info('Configured lights: "{}"'. format(self.lights))

    def _expand_groups(self, group_names):
        groups = [g for g in self.bridge.groups
                if g.name in group_names]

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

    def _execute(self, attr, *args, **kwargs):
        try:
            self.connect()
        except Exception as e:
            logging.exception(e)
            # Reset bridge connection
            self.bridge = None
            return

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

        logging.info('[Attribute: {}] [Values: {}] [Lights: {}] [Groups: {}]'.
                     format(attr, args, lights, groups))

        try:
            if attr == 'scene':
                self.bridge.run_scene(groups[0], kwargs['name'])
            elif groups:
                self.bridge.set_group(groups, attr, *args)
            elif lights:
                self.bridge.set_light(lights, attr, *args)
        except Exception as e:
            print(e)
            logging.exception(e)
            # Reset bridge connection
            self.bridge = None

    def on(self, lights=[], groups=[]):
        self._execute('on', True, lights=lights, groups=groups)

    def off(self, lights=[], groups=[]):
        self._execute('on', False, lights=lights, groups=groups)

    def bri(self, value, lights=[], groups=[]):
        self._execute('bri', int(value) % (self.MAX_BRI+1),
                      lights=lights, groups=groups)

    def sat(self, value, lights=[], groups=[]):
        self._execute('sat', int(value) % (self.MAX_SAT+1),
                      lights=lights, groups=groups)

    def hue(self, value, lights=[], groups=[]):
        self._execute('hue', int(value) % (self.MAX_HUE+1),
                      lights=lights, groups=groups)

    def hue(self, value, lights=[], groups=[]):
        self._execute('hue', int(value) % (self.MAX_HUE+1),
                      lights=lights, groups=groups)

    def scene(self, name, lights=[], groups=[]):
        self._execute('scene', name=name, lights=lights, groups=groups)

    def status(self):
        return ['']

# vim:sw=4:ts=4:et:

