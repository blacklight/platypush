import random
import time

from enum import Enum
from threading import Thread
from redis import Redis
from redis.exceptions import TimeoutError as QueueTimeoutError
from phue import Bridge

from platypush.context import get_backend
from platypush.plugins import action
from platypush.plugins.light import LightPlugin


class LightHuePlugin(LightPlugin):
    """
    Philips Hue lights plugin.

    Requires:

        * **phue** (``pip install phue``)
    """

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
        :param bridge: Bridge address or hostname
        :type bridge: str

        :param lights: Default lights to be controlled (default: all)
        :type lights: list[str]

        :param groups Default groups to be controlled (default: all)
        :type groups: list[str]
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

    @action
    def connect(self):
        """
        Connect to the configured Hue bridge. If the device hasn't been paired
        yet, uncomment the ``.connect()`` and ``.get_api()`` lines and retry
        after clicking the pairing button on your bridge.

        :todo: Support for dynamic retry and better user interaction in case of bridge pairing neeeded.
        """

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


    @action
    def get_scenes(self):
        """
        Get the available scenes on the devices.

        :returns: The scenes configured on the bridge.

        Example output::

            output = {
                "scene-id-1": {
                    "name": "Scene 1",
                    "lights": [
                        "1",
                        "3"
                    ],
                    "owner": "owner-id",
                    "recycle": true,
                    "locked": false,
                    "appdata": {},
                    "picture": "",
                    "lastupdated": "2018-06-01T00:00:00",
                    "version": 1
                },
                "scene-id-2": {
                    # ...
                }
            }
        """

        return self.bridge.get_scene()


    @action
    def get_lights(self):
        """
        Get the configured lights.

        :returns: List of available lights as id->dict.

        Example::

            output = {
                "1": {
                    "state": {
                        "on": true,
                        "bri": 254,
                        "hue": 1532,
                        "sat": 215,
                        "effect": "none",
                        "xy": [
                            0.6163,
                            0.3403
                        ],
                        "ct": 153,
                        "alert": "none",
                        "colormode": "hs",
                        "reachable": true
                    },
                    "type": "Extended color light",
                    "name": "Lightbulb 1",
                    "modelid": "LCT001",
                    "manufacturername": "Philips",
                    "uniqueid": "00:11:22:33:44:55:66:77-88",
                    "swversion": "5.105.0.21169"
                },
                "2": {
                    # ...
                }
            }
        """

        return self.bridge.get_light()


    @action
    def get_groups(self):
        """
        Get the list of configured light groups.

        :returns: List of configured light groups as id->dict.

        Example::

            output = {
                "1": {
                    "name": "Living Room",
                    "lights": [
                        "16",
                        "13",
                        "12",
                        "11",
                        "10",
                        "9",
                        "1",
                        "3"
                    ],
                    "type": "Room",
                    "state": {
                        "all_on": true,
                        "any_on": true
                    },
                    "class": "Living room",
                    "action": {
                        "on": true,
                        "bri": 241,
                        "hue": 37947,
                        "sat": 221,
                        "effect": "none",
                        "xy": [
                            0.2844,
                            0.2609
                        ],
                        "ct": 153,
                        "alert": "none",
                        "colormode": "hs"
                    }
                },

                "2": {
                    # ...
                }
            }
        """

        return self.bridge.get_group()


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
                self.bridge.set_group(groups, attr, *args)
            elif lights:
                self.bridge.set_light(lights, attr, *args)
        except Exception as e:
            # Reset bridge connection
            self.bridge = None
            raise e


    @action
    def set_light(self, light, **kwargs):
        """
        Set a light (or lights) property.

        :param light: Light or lights to set. Can be a string representing the light name, a light object, a list of string, or a list of light objects.
        :param kwargs: key-value list of parameters to set.

        Example call::

            {
                "type": "request",
                "target": "hostname",
                "action": "light.hue.set_light",
                "args": {
                    "light": "Bulb 1",
                    "sat": 255
                }
            }
        """

        self.connect()
        self.bridge.set_light(light, **kwargs)

    @action
    def set_group(self, group, **kwargs):
        """
        Set a group (or groups) property.

        :param group: Group or groups to set. Can be a string representing the group name, a group object, a list of strings, or a list of group objects.
        :param kwargs: key-value list of parameters to set.

        Example call::

            {
                "type": "request",
                "target": "hostname",
                "action": "light.hue.set_group",
                "args": {
                    "light": "Living Room",
                    "sat": 255
                }
            }
        """

        self.connect()
        self.bridge.set_group(group, **kwargs)

    @action
    def on(self, lights=[], groups=[]):
        """
        Turn lights/groups on.

        :param lights: Lights to turn on (names or light objects). Default: plugin default lights
        :param groups: Groups to turn on (names or group objects). Default: plugin default groups
        """

        return self._exec('on', True, lights=lights, groups=groups)

    @action
    def off(self, lights=[], groups=[]):
        """
        Turn lights/groups off.

        :param lights: Lights to turn off (names or light objects). Default: plugin default lights
        :param groups: Groups to turn off (names or group objects). Default: plugin default groups
        """

        return self._exec('on', False, lights=lights, groups=groups)

    @action
    def bri(self, value, lights=[], groups=[]):
        """
        Set lights/groups brightness.

        :param lights: Lights to control (names or light objects). Default: plugin default lights
        :param groups: Groups to control (names or group objects). Default: plugin default groups
        :param value: Brightness value (range: 0-255)
        """

        return self._exec('bri', int(value) % (self.MAX_BRI+1),
                      lights=lights, groups=groups)

    @action
    def sat(self, value, lights=[], groups=[]):
        """
        Set lights/groups saturation.

        :param lights: Lights to control (names or light objects). Default: plugin default lights
        :param groups: Groups to control (names or group objects). Default: plugin default groups
        :param value: Saturation value (range: 0-255)
        """

        return self._exec('sat', int(value) % (self.MAX_SAT+1),
                      lights=lights, groups=groups)

    @action
    def hue(self, value, lights=[], groups=[]):
        """
        Set lights/groups color hue.

        :param lights: Lights to control (names or light objects). Default: plugin default lights
        :param groups: Groups to control (names or group objects). Default: plugin default groups
        :param value: Hue value (range: 0-65535)
        """

        return self._exec('hue', int(value) % (self.MAX_HUE+1),
                      lights=lights, groups=groups)

    @action
    def scene(self, name, lights=[], groups=[]):
        """
        Set a scene by name.

        :param lights: Lights to control (names or light objects). Default: plugin default lights
        :param groups: Groups to control (names or group objects). Default: plugin default groups
        :param name: Name of the scene
        """

        return self._exec('scene', name=name, lights=lights, groups=groups)

    @action
    def is_animation_running(self):
        """
        :returns: True if there is an animation running, false otherwise.
        """

        return self.animation_thread is not None

    @action
    def stop_animation(self):
        """
        Stop a running animation if any
        """

        if self.animation_thread and self.animation_thread.is_alive():
            self.redis.rpush(self.ANIMATION_CTRL_QUEUE_NAME, 'STOP')

    @action
    def animate(self, animation, duration=None,
                hue_range=[0, MAX_HUE], sat_range=[0, MAX_SAT],
                bri_range=[MAX_BRI-1, MAX_BRI], lights=None, groups=None,
                hue_step=1000, sat_step=2, bri_step=1, transition_seconds=1.0):
        """
        Run a lights animation.

        :param animation: Animation name. Supported types: **color_transition** and **blink**
        :type animation: str

        :param duration: Animation duration in seconds (default: None, i.e. continue until stop)
        :type duration: float

        :param hue_range: If you selected a color transition, this will specify the hue range of your color transition. Default: [0, 65535]
        :type hue_range: list[int]

        :param sat_range: If you selected a color transition, this will specify the saturation range of your color transition. Default: [0, 255]
        :type sat_range: list[int]

        :param bri_range: If you selected a color transition, this will specify the brightness range of your color transition. Default: [254, 255]
        :type bri_range: list[int]

        :param lights: Lights to control (names or light objects). Default: plugin default lights
        :param groups: Groups to control (names or group objects). Default: plugin default groups

        :param hue_step: If you selected a color transition, this will specify by how much the color hue will change between iterations. Default: 1000
        :type hue_step: int

        :param sat_step: If you selected a color transition, this will specify by how much the saturation will change between iterations. Default: 2
        :type sat_step: int

        :param bri_step: If you selected a color transition, this will specify by how much the brightness will change between iterations. Default: 1
        :type bri_step: int

        :param transition_seconds: Time between two transitions or blinks in seconds. Default: 1.0
        :type treansition_seconds: float
        """


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

                try:
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
                except Exception as e:
                    self.logger.warning(e)
                    time.sleep(2)

                lights = _next_light_attrs(lights)

            self.logger.info('Stopping animation')
            self.animation_thread = None
            self.redis = None

        redis_args = get_backend('redis').redis_args
        redis_args['socket_timeout'] = transition_seconds
        self.redis = Redis(**redis_args)

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


# vim:sw=4:ts=4:et:

