import random
import time

from enum import Enum
from threading import Thread
from redis import Redis
from redis.exceptions import TimeoutError as QueueTimeoutError
from phue import Bridge

from platypush.message.response import Response

from .. import LightPlugin

class LightHuePlugin(LightPlugin):
    """ Philips Hue lights plugin """

    MAX_BRI = 255
    MAX_SAT = 255
    MAX_HUE = 65535
    ANIMATION_CTRL_QUEUE_NAME = 'platypush/light/hue/AnimationCtrl'

    class Animation(Enum):
        COLOR_TRANSITION = 'color_transition'
        BLINK = 'blink'

        def __eq__(self, other):
            if isinstance(other, str):
                return self.value == other
            elif isinstance(other, self.__class__):
                return self == other

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
        self.logger.info('Initializing Hue lights plugin - bridge: "{}"'.
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

        self.redis = None
        self.animation_thread = None
        self.logger.info('Configured lights: "{}"'. format(self.lights))

    def _expand_groups(self):
        groups = [g for g in self.bridge.groups if g.name in self.groups]
        for g in groups:
            self.lights.extend([l.name for l in g.lights])

    def connect(self):
        # Lazy init
        if not self.bridge:
            self.bridge = Bridge(self.bridge_address)
            self.logger.info('Bridge connected')

            self.get_scenes()

            # uncomment these lines if you're running huectrl for
            # the first time and you need to pair it to the switch

            # self.bridge.connect()
            # self.bridge.get_api()
        else:
            self.logger.info('Bridge already connected')


    def get_scenes(self):
        return Response(output=self.bridge.get_scene())


    def get_lights(self):
        return Response(output=self.bridge.get_light())


    def get_groups(self):
        return Response(output=self.bridge.get_group())


    def _exec(self, attr, *args, **kwargs):
        try:
            self.connect()
            self.stop_animation()
        except Exception as e:
            # Reset bridge connection
            self.bridge = None
            raise e

        lights = []; groups = []
        if 'lights' in kwargs and kwargs['lights']:
            lights = kwargs.pop('lights').split(',').strip() \
                if isinstance(lights, str) else kwargs.pop('lights')
        elif 'groups' in kwargs and kwargs['groups']:
            groups = kwargs.pop('groups').split(',').strip() \
                if isinstance(groups, str) else kwargs.pop('groups')
        else:
            lights = self.lights
            groups = self.groups

        try:
            if attr == 'scene':
                self.bridge.run_scene(groups[0], kwargs.pop('name'))
            elif groups:
                self.bridge.set_group(groups, attr, *args, **kwargs)
            elif lights:
                self.bridge.set_light(lights, attr, *args, **kwargs)
        except Exception as e:
            # Reset bridge connection
            self.bridge = None
            raise e

        return Response(output='ok')

    def set_light(self, light, **kwargs):
        self.connect()
        self.bridge.set_light(light, **kwargs)
        return Response(output='ok')

    def set_group(self, group, **kwargs):
        self.connect()
        self.bridge.set_group(group, **kwargs)
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

    def stop_animation(self):
        if self.animation_thread and self.animation_thread.is_alive():
            self.redis.rpush(self.ANIMATION_CTRL_QUEUE_NAME, 'STOP')

    def animate(self, animation, duration=None,
                hue_range=[0, MAX_HUE], sat_range=[0, MAX_SAT],
                bri_range=[MAX_BRI-1, MAX_BRI], lights=None, groups=None,
                hue_step=1000, sat_step=2, bri_step=1, transition_seconds=1.0):

        def _initialize_light_attrs(lights):
            if animation == self.Animation.COLOR_TRANSITION:
                return { l: {
                    'hue': random.randint(hue_range[0], hue_range[1]),
                    'sat': random.randint(sat_range[0], sat_range[1]),
                    'bri': random.randint(bri_range[0], bri_range[1]),
                } for l in lights }
            elif animation == self.Animation.BLINK:
                return { l: {
                    'on': True,
                    'bri': self.MAX_BRI,
                    'transitiontime': 0,
                } for l in lights }


        def _next_light_attrs(lights):
            if animation == self.Animation.COLOR_TRANSITION:
                for (light, attrs) in lights.items():
                    for (attr, value) in attrs.items():
                        if attr == 'hue':
                            attr_range = hue_range
                            attr_step = hue_step
                        elif attr == 'bri':
                            attr_range = bri_range
                            attr_step = bri_step
                        elif attr == 'sat':
                            attr_range = sat_range
                            attr_step = sat_step

                        lights[light][attr] = ((value - attr_range[0] + attr_step) %
                                                (attr_range[1]-attr_range[0]+1)) + \
                                                attr_range[0]
            elif animation == self.Animation.BLINK:
                lights = { light: {
                    'on': False if attrs['on'] else True,
                    'bri': self.MAX_BRI,
                    'transitiontime': 0,
                } for (light, attrs) in lights.items() }

            return lights

        def _should_stop():
            try:
                self.redis.blpop(self.ANIMATION_CTRL_QUEUE_NAME)
                return True
            except QueueTimeoutError:
                return False


        def _animate_thread(lights):
            self.logger.info('Starting {} animation'.format(
                animation, (lights or groups)))

            lights = _initialize_light_attrs(lights)
            animation_start_time = time.time()
            stop_animation = False

            while True:
                if stop_animation or \
                        (duration and time.time() - animation_start_time > duration):
                    break

                if animation == self.Animation.COLOR_TRANSITION:
                    for (light, attrs) in lights.items():
                        self.logger.info('Setting {} to {}'.format(light, attrs))
                        self.bridge.set_light(light, attrs)
                        stop_animation = _should_stop()
                        if stop_animation: break
                elif animation == self.Animation.BLINK:
                    conf = lights[list(lights.keys())[0]]
                    self.logger.info('Setting lights to {}'.format(conf))

                    if groups:
                        self.bridge.set_group([g.name for f in groups], conf)
                    else:
                        self.bridge.set_light(lights.keys(), conf)

                    stop_animation = _should_stop()
                    if stop_animation: break

                lights = _next_light_attrs(lights)

            self.logger.info('Stopping animation')
            self.animation_thread = None
            self.redis = None

        self.redis = Redis(socket_timeout=transition_seconds)

        if groups:
            groups = [g for g in self.bridge.groups if g.name in groups]
            lights = lights or []
            for g in groups:
                lights.extend([l.name for l in g.lights])
        elif not lights:
            lights = self.lights

        self.stop_animation()
        self.animation_thread = Thread(target=_animate_thread, args=(lights,))
        self.animation_thread.start()
        return Response(output='ok')


# vim:sw=4:ts=4:et:

