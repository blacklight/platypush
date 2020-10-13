import random
import statistics
import time

from enum import Enum
from threading import Thread, Event

from platypush.plugins import action
from platypush.plugins.light import LightPlugin
from platypush.utils import set_thread_name


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
    _BRIDGE_RECONNECT_SECONDS = 5
    _MAX_RECONNECT_TRIES = 5

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
        self.logger.info('Initializing Hue lights plugin - bridge: "{}"'.format(self.bridge_address))

        self.connect()
        self.lights = []
        self.groups = []

        if lights:
            self.lights = lights
        elif groups:
            self.groups = groups
            self._expand_groups()
        else:
            # noinspection PyUnresolvedReferences
            self.lights = [light.name for light in self.bridge.lights]

        self.animation_thread = None
        self.animations = {}
        self._animation_stop = Event()
        self._init_animations()
        self.logger.info('Configured lights: "{}"'.format(self.lights))

    def _expand_groups(self):
        groups = [g for g in self.bridge.groups if g.name in self.groups]
        for group in groups:
            for light in group.lights:
                self.lights += [light.name]

    def _init_animations(self):
        self.animations = {
            'groups': {},
            'lights': {},
        }

        for group in self.bridge.groups:
            self.animations['groups'][group.group_id] = None
        for light in self.bridge.lights:
            self.animations['lights'][light.light_id] = None

    @action
    def connect(self):
        """
        Connect to the configured Hue bridge. If the device hasn't been paired
        yet, uncomment the ``.connect()`` and ``.get_api()`` lines and retry
        after clicking the pairing button on your bridge.
        """

        # Lazy init
        if not self.bridge:
            from phue import Bridge, PhueRegistrationException
            success = False
            n_tries = 0

            while not success:
                try:
                    n_tries += 1
                    self.bridge = Bridge(self.bridge_address)
                    success = True
                except PhueRegistrationException as e:
                    self.logger.warning('Bridge registration error: {}'.
                                        format(str(e)))

                    if n_tries >= self._MAX_RECONNECT_TRIES:
                        self.logger.error(('Bridge registration failed after ' +
                                           '{} attempts').format(n_tries))
                        break

                    time.sleep(self._BRIDGE_RECONNECT_SECONDS)

            self.logger.info('Bridge connected')
            self.get_scenes()
        else:
            self.logger.info('Bridge already connected')

    @action
    def get_scenes(self):
        """
        Get the available scenes on the devices.

        :returns: The scenes configured on the bridge.

        Example output::

            {
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

            {
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

            {
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
                }
            }

        """

        return self.bridge.get_group()

    @action
    def get_animations(self):
        """
        Get the list of running light animations.

        :returns: dict.

        Structure::

            {
                "groups": {
                    "id_1": {
                        "type": "color_transition",
                        "hue_range": [0,65535],
                        "sat_range": [0,255],
                        "bri_range": [0,255],
                        "hue_step": 10,
                        "sat_step": 10,
                        "bri_step": 2,
                        "transition_seconds": 2

                    }

                },

                "lights": {
                    "id_1": {}

                }

            }

        """

        return self.animations

    def _exec(self, attr, *args, **kwargs):
        try:
            self.connect()
            self.stop_animation()
        except Exception as e:
            # Reset bridge connection
            self.bridge = None
            raise e

        lights = []
        groups = []

        if 'lights' in kwargs:
            lights = kwargs.pop('lights').split(',').strip() \
                if isinstance(lights, str) else kwargs.pop('lights')
        if 'groups' in kwargs:
            groups = kwargs.pop('groups').split(',').strip() \
                if isinstance(groups, str) else kwargs.pop('groups')

        if not lights and not groups:
            lights = self.lights
            groups = self.groups

        if not self.bridge:
            self.connect()

        try:
            if attr == 'scene':
                self.bridge.run_scene(groups[0], kwargs.pop('name'))
            else:
                if groups:
                    self.bridge.set_group(groups, attr, *args, **kwargs)
                if lights:
                    self.bridge.set_light(lights, attr, *args, **kwargs)
        except Exception as e:
            # Reset bridge connection
            self.bridge = None
            raise e

    @action
    def set_light(self, light, **kwargs):
        """
        Set a light (or lights) property.

        :param light: Light or lights to set. Can be a string representing the light name,
            a light object, a list of string, or a list of light objects.
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
    def on(self, lights=None, groups=None, **kwargs):
        """
        Turn lights/groups on.

        :param lights: Lights to turn on (names or light objects). Default: plugin default lights
        :param groups: Groups to turn on (names or group objects). Default: plugin default groups
        """

        if groups is None:
            groups = []
        if lights is None:
            lights = []
        return self._exec('on', True, lights=lights, groups=groups, **kwargs)

    @action
    def off(self, lights=None, groups=None, **kwargs):
        """
        Turn lights/groups off.

        :param lights: Lights to turn off (names or light objects). Default: plugin default lights
        :param groups: Groups to turn off (names or group objects). Default: plugin default groups
        """

        if groups is None:
            groups = []
        if lights is None:
            lights = []
        return self._exec('on', False, lights=lights, groups=groups, **kwargs)

    @action
    def toggle(self, lights=None, groups=None, **kwargs):
        """
        Toggle lights/groups on/off.

        :param lights: Lights to turn off (names or light objects). Default: plugin default lights
        :param groups: Groups to turn off (names or group objects). Default: plugin default groups
        """

        if groups is None:
            groups = []
        if lights is None:
            lights = []
        lights_on = []
        lights_off = []
        groups_on = []
        groups_off = []

        if groups:
            all_groups = self.bridge.get_group().values()

            groups_on = [
                group['name'] for group in all_groups
                if group['name'] in groups and group['state']['any_on'] is True
            ]

            groups_off = [
                group['name'] for group in all_groups
                if group['name'] in groups and group['state']['any_on'] is False
            ]

        if not groups and not lights:
            lights = self.lights

        if lights:
            all_lights = self.bridge.get_light().values()

            lights_on = [
                light['name'] for light in all_lights
                if light['name'] in lights and light['state']['on'] is True
            ]

            lights_off = [
                light['name'] for light in all_lights
                if light['name'] in lights and light['state']['on'] is False
            ]

        if lights_on or groups_on:
            self._exec('on', False, lights=lights_on, groups=groups_on, **kwargs)

        if lights_off or groups_off:
            self._exec('on', True, lights=lights_off, groups=groups_off, **kwargs)

    @action
    def bri(self, value, lights=None, groups=None, **kwargs):
        """
        Set lights/groups brightness.

        :param lights: Lights to control (names or light objects). Default: plugin default lights
        :param groups: Groups to control (names or group objects). Default: plugin default groups
        :param value: Brightness value (range: 0-255)
        """

        if groups is None:
            groups = []
        if lights is None:
            lights = []
        return self._exec('bri', int(value) % (self.MAX_BRI + 1),
                          lights=lights, groups=groups, **kwargs)

    @action
    def sat(self, value, lights=None, groups=None, **kwargs):
        """
        Set lights/groups saturation.

        :param lights: Lights to control (names or light objects). Default: plugin default lights
        :param groups: Groups to control (names or group objects). Default: plugin default groups
        :param value: Saturation value (range: 0-255)
        """

        if groups is None:
            groups = []
        if lights is None:
            lights = []
        return self._exec('sat', int(value) % (self.MAX_SAT + 1),
                          lights=lights, groups=groups, **kwargs)

    @action
    def hue(self, value, lights=None, groups=None, **kwargs):
        """
        Set lights/groups color hue.

        :param lights: Lights to control (names or light objects). Default: plugin default lights
        :param groups: Groups to control (names or group objects). Default: plugin default groups
        :param value: Hue value (range: 0-65535)
        """

        if groups is None:
            groups = []
        if lights is None:
            lights = []
        return self._exec('hue', int(value) % (self.MAX_HUE + 1),
                          lights=lights, groups=groups, **kwargs)

    @action
    def xy(self, value, lights=None, groups=None, **kwargs):
        """
        Set lights/groups XY colors.

        :param value: xY value
        :type value: list[float] containing the two values
        :param lights: List of lights.
        :param groups: List of groups.
        """
        if groups is None:
            groups = []
        if lights is None:
            lights = []
        return self._exec('xy', value, lights=lights, groups=groups, **kwargs)

    @action
    def ct(self, value, lights=None, groups=None, **kwargs):
        """
        Set lights/groups color temperature.

        :param value: Temperature value (range: 0-255)
        :type value: int
        :param lights: List of lights.
        :param groups: List of groups.
        """
        if groups is None:
            groups = []
        if lights is None:
            lights = []
        return self._exec('ct', value, lights=lights, groups=groups, **kwargs)

    @action
    def delta_bri(self, delta, lights=None, groups=None, **kwargs):
        """
        Change lights/groups brightness by a delta [-100, 100] compared to the current state.

        :param lights: Lights to control (names or light objects). Default: plugin default lights
        :param groups: Groups to control (names or group objects). Default: plugin default groups
        :param delta: Brightness delta value (range: -100, 100)
        """

        if groups is None:
            groups = []
        if lights is None:
            lights = []

        if lights:
            bri = statistics.mean([
                light['state']['bri']
                for light in self.bridge.get_light().values()
                if light['name'] in lights
            ])
        elif groups:
            bri = statistics.mean([
                group['action']['bri']
                for group in self.bridge.get_group().values()
                if group['name'] in groups
            ])
        else:
            bri = statistics.mean([
                light['state']['bri']
                for light in self.bridge.get_light().values()
                if light['name'] in self.lights
            ])

        delta *= (self.MAX_BRI / 100)
        if bri + delta < 0:
            bri = 0
        elif bri + delta > self.MAX_BRI:
            bri = self.MAX_BRI
        else:
            bri += delta

        return self._exec('bri', int(bri), lights=lights, groups=groups, **kwargs)

    @action
    def delta_sat(self, delta, lights=None, groups=None, **kwargs):
        """
        Change lights/groups saturation by a delta [-100, 100] compared to the current state.

        :param lights: Lights to control (names or light objects). Default: plugin default lights
        :param groups: Groups to control (names or group objects). Default: plugin default groups
        :param delta: Saturation delta value (range: -100, 100)
        """

        if groups is None:
            groups = []
        if lights is None:
            lights = []

        if lights:
            sat = statistics.mean([
                light['state']['sat']
                for light in self.bridge.get_light().values()
                if light['name'] in lights
            ])
        elif groups:
            sat = statistics.mean([
                group['action']['sat']
                for group in self.bridge.get_group().values()
                if group['name'] in groups
            ])
        else:
            sat = statistics.mean([
                light['state']['sat']
                for light in self.bridge.get_light().values()
                if light['name'] in self.lights
            ])

        delta *= (self.MAX_SAT / 100)
        if sat + delta < 0:
            sat = 0
        elif sat + delta > self.MAX_SAT:
            sat = self.MAX_SAT
        else:
            sat += delta

        return self._exec('sat', int(sat), lights=lights, groups=groups, **kwargs)

    @action
    def delta_hue(self, delta, lights=None, groups=None, **kwargs):
        """
        Change lights/groups hue by a delta [-100, 100] compared to the current state.

        :param lights: Lights to control (names or light objects). Default: plugin default lights
        :param groups: Groups to control (names or group objects). Default: plugin default groups
        :param delta: Hue delta value (range: -100, 100)
        """

        if groups is None:
            groups = []
        if lights is None:
            lights = []

        if lights:
            hue = statistics.mean([
                light['state']['hue']
                for light in self.bridge.get_light().values()
                if light['name'] in lights
            ])
        elif groups:
            hue = statistics.mean([
                group['action']['hue']
                for group in self.bridge.get_group().values()
                if group['name'] in groups
            ])
        else:
            hue = statistics.mean([
                light['state']['hue']
                for light in self.bridge.get_light().values()
                if light['name'] in self.lights
            ])

        delta *= (self.MAX_HUE / 100)
        if hue + delta < 0:
            hue = 0
        elif hue + delta > self.MAX_HUE:
            hue = self.MAX_HUE
        else:
            hue += delta

        return self._exec('hue', int(hue), lights=lights, groups=groups, **kwargs)

    @action
    def scene(self, name, lights=None, groups=None, **kwargs):
        """
        Set a scene by name.

        :param lights: Lights to control (names or light objects). Default: plugin default lights
        :param groups: Groups to control (names or group objects). Default: plugin default groups
        :param name: Name of the scene
        """

        if groups is None:
            groups = []
        if lights is None:
            lights = []
        return self._exec('scene', name=name, lights=lights, groups=groups, **kwargs)

    @action
    def is_animation_running(self):
        """
        :returns: True if there is an animation running, false otherwise.
        """

        return self.animation_thread is not None and self.animation_thread.is_alive()

    @action
    def stop_animation(self):
        """
        Stop a running animation.
        """
        if self.is_animation_running():
            self._animation_stop.set()
            self._init_animations()

    @action
    def animate(self, animation, duration=None,
                hue_range=None, sat_range=None,
                bri_range=None, lights=None, groups=None,
                hue_step=1000, sat_step=2, bri_step=1, transition_seconds=1.0):
        """
        Run a lights animation.

        :param animation: Animation name. Supported types: **color_transition** and **blink**
        :type animation: str

        :param duration: Animation duration in seconds (default: None, i.e. continue until stop)
        :type duration: float

        :param hue_range: If you selected a color color_transition.html, this will specify the hue range of your color color_transition.html.
            Default: [0, 65535]
        :type hue_range: list[int]

        :param sat_range: If you selected a color color_transition.html, this will specify the saturation range of your color
            color_transition.html. Default: [0, 255]
        :type sat_range: list[int]

        :param bri_range: If you selected a color color_transition.html, this will specify the brightness range of your color
            color_transition.html. Default: [254, 255] :type bri_range: list[int]

        :param lights: Lights to control (names, IDs or light objects). Default: plugin default lights
        :param groups: Groups to control (names, IDs or group objects). Default: plugin default groups

        :param hue_step: If you selected a color color_transition.html, this will specify by how much the color hue will change
            between iterations. Default: 1000 :type hue_step: int

        :param sat_step: If you selected a color color_transition.html, this will specify by how much the saturation will change
            between iterations. Default: 2 :type sat_step: int

        :param bri_step: If you selected a color color_transition.html, this will specify by how much the brightness will change
            between iterations. Default: 1 :type bri_step: int

        :param transition_seconds: Time between two transitions or blinks in seconds. Default: 1.0
        :type transition_seconds: float
        """

        if bri_range is None:
            bri_range = [self.MAX_BRI - 1, self.MAX_BRI]
        if sat_range is None:
            sat_range = [0, self.MAX_SAT]
        if hue_range is None:
            hue_range = [0, self.MAX_HUE]
        if groups:
            groups = [g for g in self.bridge.groups if g.name in groups or g.group_id in groups]
            lights = lights or []
            for group in groups:
                lights.extend([light.name for light in group.lights])
        elif lights:
            lights = [light.name for light in self.bridge.lights if light.name in lights or light.light_id in lights]
        else:
            lights = self.lights

        info = {
            'type': animation,
            'duration': duration,
            'hue_range': hue_range,
            'sat_range': sat_range,
            'bri_range': bri_range,
            'hue_step': hue_step,
            'sat_step': sat_step,
            'bri_step': bri_step,
            'transition_seconds': transition_seconds,
        }

        if groups:
            for group in groups:
                self.animations['groups'][group.group_id] = info

        for light in self.bridge.lights:
            if light.name in lights:
                self.animations['lights'][light.light_id] = info

        def _initialize_light_attrs(lights):
            if animation == self.Animation.COLOR_TRANSITION:
                return {light: {
                    'hue': random.randint(hue_range[0], hue_range[1]),
                    'sat': random.randint(sat_range[0], sat_range[1]),
                    'bri': random.randint(bri_range[0], bri_range[1]),
                } for light in lights}
            elif animation == self.Animation.BLINK:
                return {light: {
                    'on': True,
                    'bri': self.MAX_BRI,
                    'transitiontime': 0,
                } for light in lights}

        def _next_light_attrs(lights):
            if animation == self.Animation.COLOR_TRANSITION:
                for (light, attrs) in lights.items():
                    for (attr, value) in attrs.items():
                        attr_range = [0, 0]
                        attr_step = 0

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
                                               (attr_range[1] - attr_range[0] + 1)) + \
                                              attr_range[0]
            elif animation == self.Animation.BLINK:
                lights = {light: {
                    'on': False if attrs['on'] else True,
                    'bri': self.MAX_BRI,
                    'transitiontime': 0,
                } for (light, attrs) in lights.items()}

            return lights

        def _should_stop():
            return self._animation_stop.is_set()

        def _animate_thread(lights):
            set_thread_name('HueAnimate')
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
                            self.logger.debug('Setting {} to {}'.format(light, attrs))
                            self.bridge.set_light(light, attrs)
                            stop_animation = _should_stop()
                            if stop_animation: break
                    elif animation == self.Animation.BLINK:
                        conf = lights[list(lights.keys())[0]]
                        self.logger.debug('Setting lights to {}'.format(conf))

                        if groups:
                            self.bridge.set_group([g.name for g in groups], conf)
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

        self.stop_animation()
        self._animation_stop.clear()
        self.animation_thread = Thread(target=_animate_thread,
                                       name='HueAnimate',
                                       args=(lights,))
        self.animation_thread.start()

    def status(self):
        # TODO
        pass

# vim:sw=4:ts=4:et:
