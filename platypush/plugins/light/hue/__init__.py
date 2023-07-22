import random
import statistics
import time

from enum import Enum
from threading import Thread, Event
from typing import (
    Any,
    Collection,
    Dict,
    Iterable,
    Mapping,
    Set,
    Union,
)
import warnings

from platypush.context import get_bus
from platypush.entities import Entity, LightEntityManager
from platypush.entities.lights import Light as LightEntity
from platypush.message.event.light import (
    LightAnimationStartedEvent,
    LightAnimationStoppedEvent,
    LightStatusChangeEvent,
)
from platypush.plugins import RunnablePlugin, action
from platypush.utils import set_thread_name


class LightHuePlugin(RunnablePlugin, LightEntityManager):
    """
    Philips Hue lights plugin.

    Requires:

        * **phue** (``pip install phue``)

    Triggers:

        - :class:`platypush.message.event.light.LightAnimationStartedEvent` when an animation is started.
        - :class:`platypush.message.event.light.LightAnimationStoppedEvent` when an animation is stopped.
        - :class:`platypush.message.event.light.LightStatusChangeEvent` when the status of a lightbulb
          changes.

    """

    MAX_BRI = 255
    MAX_SAT = 255
    MAX_HUE = 65535
    MIN_CT = 154
    MAX_CT = 500
    ANIMATION_CTRL_QUEUE_NAME = 'platypush/light/hue/AnimationCtrl'
    _BRIDGE_RECONNECT_SECONDS = 5
    _MAX_RECONNECT_TRIES = 5
    _UNINITIALIZED_BRIDGE_ERR = 'The Hue bridge is not initialized'

    class Animation(Enum):
        """
        Inner class to model light animations.
        """

        COLOR_TRANSITION = 'color_transition'
        BLINK = 'blink'

        def __eq__(self, other):
            """
            Check if the configuration of two light animations matches.
            """
            if isinstance(other, str):
                return self.value == other
            if isinstance(other, self.__class__):
                return self == other
            return False

    def __init__(
        self, bridge, lights=None, groups=None, poll_interval: float = 20.0, **kwargs
    ):
        """
        :param bridge: Bridge address or hostname
        :type bridge: str

        :param lights: Default lights to be controlled (default: all)
        :type lights: list[str]

        :param groups Default groups to be controlled (default: all)
        :type groups: list[str]

        :param poll_interval: How often the plugin should check the bridge for light
            updates (default: 20 seconds).
        """

        poll_seconds = kwargs.pop('poll_seconds', None)
        if poll_seconds is not None:
            warnings.warn(
                'poll_seconds is deprecated, use poll_interval instead',
                DeprecationWarning,
                stacklevel=2,
            )

            if poll_interval is None:
                poll_interval = poll_seconds

        super().__init__(**kwargs)

        self.bridge_address = bridge
        self.bridge = None
        self.logger.info(
            'Initializing Hue lights plugin - bridge: "%s"', self.bridge_address
        )

        self.connect()
        self.lights = set()
        self.groups = set()
        self.poll_interval = poll_interval
        self._cached_lights: Dict[str, dict] = {}

        if lights:
            self.lights = set(lights)
        elif groups:
            self.groups = set(groups)
            self.lights.update(self._expand_groups(self.groups))
        else:
            self.lights = {light['name'] for light in self._get_lights().values()}

        self.animation_thread = None
        self.animations: Dict[str, dict] = {}
        self._animation_stop = Event()
        self._init_animations()
        self.logger.info('Configured lights: %s', self.lights)

    def _expand_groups(self, groups: Iterable[str]) -> Set[str]:
        lights = set()
        light_id_to_name = {
            light_id: light['name'] for light_id, light in (self._get_lights().items())
        }

        groups_ = [g for g in self._get_groups().values() if g.get('name') in groups]

        for group in groups_:
            for light_id in group.get('lights', []):
                light_name = light_id_to_name.get(light_id)
                if light_name:
                    lights.add(light_name)

        return lights

    def _init_animations(self):
        self.animations = {
            'groups': {},
            'lights': {},
        }

        for group_id in self._get_groups():
            self.animations['groups'][group_id] = None
        for light_id in self._get_lights():
            self.animations['lights'][light_id] = None

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
                    self.logger.warning('Bridge registration error: %s', e)

                    if n_tries >= self._MAX_RECONNECT_TRIES:
                        self.logger.error(
                            (
                                'Bridge registration failed after ' + '{} attempts'
                            ).format(n_tries)
                        )
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

        return {
            id: {
                'id': id,
                **scene,
            }
            for id, scene in self._get_scenes().items()
        }

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

        return {
            id: {
                'id': id,
                **light,
            }
            for id, light in self._get_lights(publish_entities=True).items()
        }

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

        return {
            id: {
                'id': id,
                **group,
            }
            for id, group in self._get_groups().items()
        }

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

        assert self.bridge, self._UNINITIALIZED_BRIDGE_ERR
        lights = []
        groups = []

        if 'lights' in kwargs:
            lights = (
                kwargs.pop('lights').split(',').strip()
                if isinstance(lights, str)
                else kwargs.pop('lights')
            )
        if 'groups' in kwargs:
            groups = (
                kwargs.pop('groups').split(',').strip()
                if isinstance(groups, str)
                else kwargs.pop('groups')
            )

        if not lights and not groups:
            lights = self.lights
            groups = self.groups

        if not self.bridge:
            self.connect()

        try:
            if attr == 'scene':
                assert groups, 'No groups specified'
                self.bridge.run_scene(list(groups)[0], kwargs.pop('name'))
            else:
                if groups:
                    self.bridge.set_group(list(groups), attr, *args, **kwargs)
                if lights:
                    self.bridge.set_light(list(lights), attr, *args, **kwargs)
        except Exception as e:
            # Reset bridge connection
            self.bridge = None
            raise e

        return self._get_lights(publish_entities=True)

    @action
    def set_lights(self, lights, *_, **kwargs):  # pylint: disable=arguments-differ
        """
        Set a set of properties on a set of lights.

        :param light: List of lights to set. Each item can represent a light
            name or ID.
        :param kwargs: key-value list of the parameters to set.

        Example call::

            {
                "type": "request",
                "action": "light.hue.set_lights",
                "args": {
                    "lights": ["Bulb 1", "Bulb 2"],
                    "sat": 255
                }
            }

        """

        self.connect()
        assert self.bridge, self._UNINITIALIZED_BRIDGE_ERR
        all_lights = self._get_lights()

        for i, l in enumerate(lights):
            if str(l) in all_lights:
                lights[i] = all_lights[str(l)]['name']

        # Convert entity attributes to local attributes
        if kwargs.get('saturation') is not None:
            kwargs['sat'] = kwargs.pop('saturation')
        if kwargs.get('brightness') is not None:
            kwargs['bri'] = kwargs.pop('brightness')
        if kwargs.get('temperature') is not None:
            kwargs['ct'] = kwargs.pop('temperature')

        # "Unroll" the map
        args = []
        for arg, value in kwargs.items():
            args += [arg, value]

        assert len(args) > 1, 'Not enough parameters passed to set_lights'
        param = args.pop(0)
        value = args.pop(0)
        self.bridge.set_light(lights, param, value, *args)
        return self._get_lights(publish_entities=True)

    @action
    def set_group(self, group, **kwargs):
        """
        Set a group (or groups) property.

        :param group: Group or groups to set. Can be a string representing the
            group name, a group object, a list of strings, or a list of group
            objects.
        :param kwargs: key-value list of parameters to set.

        Example call::

            {
                "type": "request",
                "action": "light.hue.set_group",
                "args": {
                    "light": "Living Room",
                    "sat": 255
                }
            }

        """

        self.connect()
        assert self.bridge, self._UNINITIALIZED_BRIDGE_ERR
        self.bridge.set_group(group, **kwargs)

    @action
    def on(  # pylint: disable=arguments-differ
        self, lights=None, groups=None, **kwargs
    ):
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
    def off(  # pylint: disable=arguments-differ
        self, lights=None, groups=None, **kwargs
    ):
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
    def toggle(  # pylint: disable=arguments-differ
        self, lights=None, groups=None, **kwargs
    ):
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
            all_groups = self._get_groups().values()
            groups_on = [
                group['name']
                for group in all_groups
                if group['name'] in groups and group['state']['any_on'] is True
            ]

            groups_off = [
                group['name']
                for group in all_groups
                if group['name'] in groups and group['state']['any_on'] is False
            ]

        if not groups and not lights:
            lights = self.lights

        if lights:
            all_lights = self._get_lights()

            lights_on = [
                light['name']
                for light_id, light in all_lights.items()
                if (light_id in lights or light['name'] in lights)
                and light['state']['on'] is True
            ]

            lights_off = [
                light['name']
                for light_id, light in all_lights.items()
                if (light_id in lights or light['name'] in lights)
                and light['state']['on'] is False
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
        return self._exec(
            'bri',
            int(value) % (self.MAX_BRI + 1),
            lights=lights,
            groups=groups,
            **kwargs,
        )

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
        return self._exec(
            'sat',
            int(value) % (self.MAX_SAT + 1),
            lights=lights,
            groups=groups,
            **kwargs,
        )

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
        return self._exec(
            'hue',
            int(value) % (self.MAX_HUE + 1),
            lights=lights,
            groups=groups,
            **kwargs,
        )

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

        :param value: Temperature value (range: 154-500)
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
            bri = statistics.mean(
                [
                    light['state']['bri']
                    for light in self._get_lights().values()
                    if light['name'] in lights
                ]
            )
        elif groups:
            bri = statistics.mean(
                [
                    group['action']['bri']
                    for group in self._get_groups().values()
                    if group['name'] in groups
                ]
            )
        else:
            bri = statistics.mean(
                [
                    light['state']['bri']
                    for light in self._get_lights().values()
                    if light['name'] in self.lights
                ]
            )

        delta *= self.MAX_BRI / 100
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
            sat = statistics.mean(
                [
                    light['state']['sat']
                    for light in self._get_lights().values()
                    if light['name'] in lights
                ]
            )
        elif groups:
            sat = statistics.mean(
                [
                    group['action']['sat']
                    for group in self._get_groups().values()
                    if group['name'] in groups
                ]
            )
        else:
            sat = statistics.mean(
                [
                    light['state']['sat']
                    for light in self._get_lights().values()
                    if light['name'] in self.lights
                ]
            )

        delta *= self.MAX_SAT / 100
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
            hue = statistics.mean(
                [
                    light['state']['hue']
                    for light in self._get_lights().values()
                    if light['name'] in lights
                ]
            )
        elif groups:
            hue = statistics.mean(
                [
                    group['action']['hue']
                    for group in self._get_groups().values()
                    if group['name'] in groups
                ]
            )
        else:
            hue = statistics.mean(
                [
                    light['state']['hue']
                    for light in self._get_lights().values()
                    if light['name'] in self.lights
                ]
            )

        delta *= self.MAX_HUE / 100
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
    def animate(
        self,
        animation,
        duration=None,
        hue_range=None,
        sat_range=None,
        bri_range=None,
        lights=None,
        groups=None,
        hue_step=1000,
        sat_step=2,
        bri_step=1,
        transition_seconds=1.0,
    ):
        """
        Run a lights animation.

        :param animation: Animation name. Supported types: **color_transition** and **blink**
        :type animation: str

        :param duration: Animation duration in seconds (default: None, i.e. continue until stop)
        :type duration: float

        :param hue_range: If you selected a ``color_transition``, this will
            specify the hue range of your color ``color_transition``.
            Default: [0, 65535]
        :type hue_range: list[int]

        :param sat_range: If you selected a color ``color_transition``, this
            will specify the saturation range of your color
            ``color_transition``. Default: [0, 255]
        :type sat_range: list[int]

        :param bri_range: If you selected a color ``color_transition``, this
            will specify the brightness range of your color
            ``color_transition``. Default: [254, 255]
        :type bri_range: list[int]

        :param lights: Lights to control (names, IDs or light objects).
            Default: plugin default lights
        :param groups: Groups to control (names, IDs or group objects).
            Default: plugin default groups

        :param hue_step: If you selected a color ``color_transition``, this
            will specify by how much the color hue will change between
            iterations. Default: 1000
        :type hue_step: int

        :param sat_step: If you selected a color ``color_transition``, this
            will specify by how much the saturation will change
            between iterations. Default: 2
        :type sat_step: int

        :param bri_step: If you selected a color ``color_transition``, this
            will specify by how much the brightness will change between iterations.
            Default: 1
        :type bri_step: int

        :param transition_seconds: Time between two transitions or blinks in
            seconds. Default: 1.0
        :type transition_seconds: float
        """

        self.stop_animation()
        self._animation_stop.clear()
        all_lights = self._get_lights()
        bri_range = bri_range or [self.MAX_BRI - 1, self.MAX_BRI]
        sat_range = sat_range or [0, self.MAX_SAT]
        hue_range = hue_range or [0, self.MAX_HUE]

        if groups:
            groups = {
                group_id: group
                for group_id, group in self._get_groups().items()
                if group.get('name') in groups or group_id in groups
            }

            lights = set(lights or [])
            lights.update(self._expand_groups([g['name'] for g in groups.values()]))
        elif lights:
            lights = {
                light['name']
                for light_id, light in all_lights.items()
                if light['name'] in lights or int(light_id) in lights
            }
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
            for group_id in groups:
                self.animations['groups'][group_id] = info

        for light_id, light in all_lights.items():
            if light['name'] in lights:
                self.animations['lights'][light_id] = info

        def _initialize_light_attrs(lights):
            lights_by_name = {
                light['name']: light for light in self._get_lights().values()
            }

            if animation == self.Animation.COLOR_TRANSITION:
                return {
                    light: {
                        **(
                            {'hue': random.randint(hue_range[0], hue_range[1])}  # type: ignore
                            if 'hue' in lights_by_name.get(light, {}).get('state', {})
                            else {}
                        ),
                        **(
                            {'sat': random.randint(sat_range[0], sat_range[1])}  # type: ignore
                            if 'sat' in lights_by_name.get(light, {}).get('state', {})
                            else {}
                        ),
                        **(
                            {'bri': random.randint(bri_range[0], bri_range[1])}  # type: ignore
                            if 'bri' in lights_by_name.get(light, {}).get('state', {})
                            else {}
                        ),
                    }
                    for light in lights
                }
            elif animation == self.Animation.BLINK:
                return {
                    light: {
                        'on': True,
                        **({'bri': self.MAX_BRI} if 'bri' in light else {}),
                        'transitiontime': 0,
                    }
                    for light in lights
                }

            raise AssertionError(f'Unknown animation type: {animation}')

        def _next_light_attrs(lights):
            if animation == self.Animation.COLOR_TRANSITION:
                for light, attrs in lights.items():
                    for attr, value in attrs.items():
                        if attr == 'hue':
                            attr_range = hue_range
                            attr_step = hue_step
                        elif attr == 'bri':
                            attr_range = bri_range
                            attr_step = bri_step
                        elif attr == 'sat':
                            attr_range = sat_range
                            attr_step = sat_step
                        else:
                            continue

                        lights[light][attr] = (
                            (value - attr_range[0] + attr_step)
                            % (attr_range[1] - attr_range[0] + 1)
                        ) + attr_range[0]
            elif animation == self.Animation.BLINK:
                lights = {
                    light: {
                        'on': not attrs['on'],
                        'bri': self.MAX_BRI,
                        'transitiontime': 0,
                    }
                    for (light, attrs) in lights.items()
                }

            return lights

        def _should_stop():
            return self._animation_stop.is_set()

        def _animate_thread(lights):
            set_thread_name('HueAnimate')
            get_bus().post(
                LightAnimationStartedEvent(
                    lights=lights,
                    groups=list((groups or {}).keys()),
                    animation=animation,
                )
            )

            lights = _initialize_light_attrs(lights)
            animation_start_time = time.time()
            stop_animation = False

            while not stop_animation and not (
                duration and time.time() - animation_start_time > duration
            ):
                assert self.bridge, self._UNINITIALIZED_BRIDGE_ERR

                try:
                    if animation == self.Animation.COLOR_TRANSITION:
                        for light, attrs in lights.items():
                            self.logger.debug('Setting %s to %s', lights, attrs)
                            self.bridge.set_light(light, attrs)
                    elif animation == self.Animation.BLINK:
                        conf = lights[list(lights.keys())[0]]
                        self.logger.debug('Setting lights to %s', conf)

                        if groups:
                            self.bridge.set_group(
                                [g['name'] for g in groups.values()], conf
                            )
                        else:
                            self.bridge.set_light(lights.keys(), conf)

                    if transition_seconds:
                        time.sleep(transition_seconds)

                    stop_animation = _should_stop()
                except Exception as e:
                    self.logger.warning(e)
                    time.sleep(2)

                lights = _next_light_attrs(lights)

            get_bus().post(
                LightAnimationStoppedEvent(
                    lights=list(lights.keys()),
                    groups=list((groups or {}).keys()),
                    animation=animation,
                )
            )

            self.animation_thread = None

        self.animation_thread = Thread(
            target=_animate_thread, name='HueAnimate', args=(lights,)
        )
        self.animation_thread.start()

    def _get_light_attr(self, light, attr: str):
        try:
            return getattr(light, attr, None)
        except KeyError:
            return None

    def transform_entities(
        self, entities: Union[Iterable[Union[dict, Entity]], Mapping[Any, dict]]
    ) -> Collection[Entity]:
        new_entities = []
        if isinstance(entities, dict):
            entities = [{'id': id, **e} for id, e in entities.items()]

        for entity in entities:
            if isinstance(entity, Entity):
                new_entities.append(entity)
            elif isinstance(entity, dict):
                new_entities.append(
                    LightEntity(
                        id=entity['id'],
                        name=entity['name'],
                        description=entity.get('type'),
                        on=entity.get('state', {}).get('on', False),
                        brightness=entity.get('state', {}).get('bri'),
                        saturation=entity.get('state', {}).get('sat'),
                        hue=entity.get('state', {}).get('hue'),
                        temperature=entity.get('state', {}).get('ct'),
                        colormode=entity.get('colormode'),
                        reachable=entity.get('state', {}).get('reachable'),
                        x=entity['state']['xy'][0]
                        if entity.get('state', {}).get('xy')
                        else None,
                        y=entity['state']['xy'][1]
                        if entity.get('state', {}).get('xy')
                        else None,
                        effect=entity.get('state', {}).get('effect'),
                        **(
                            {
                                'hue_min': 0,
                                'hue_max': self.MAX_HUE,
                            }
                            if entity.get('state', {}).get('hue') is not None
                            else {}
                        ),
                        **(
                            {
                                'saturation_min': 0,
                                'saturation_max': self.MAX_SAT,
                            }
                            if entity.get('state', {}).get('sat') is not None
                            else {}
                        ),
                        **(
                            {
                                'brightness_min': 0,
                                'brightness_max': self.MAX_BRI,
                            }
                            if entity.get('state', {}).get('bri') is not None
                            else {}
                        ),
                        **(
                            {
                                'temperature_min': self.MIN_CT,
                                'temperature_max': self.MAX_CT,
                            }
                            if entity.get('state', {}).get('ct') is not None
                            else {}
                        ),
                    )
                )

        return new_entities

    def _get_lights(self, publish_entities=False) -> dict:
        assert self.bridge, self._UNINITIALIZED_BRIDGE_ERR
        lights = self.bridge.get_light()
        lights = {id: light for id, light in lights.items() if not light.get('recycle')}
        self._cached_lights = lights
        if publish_entities:
            self.publish_entities(lights)  # type: ignore
        return lights

    def _get_groups(self) -> dict:
        assert self.bridge, self._UNINITIALIZED_BRIDGE_ERR
        groups = self.bridge.get_group() or {}
        return {id: group for id, group in groups.items() if not group.get('recycle')}

    def _get_scenes(self) -> dict:
        assert self.bridge, self._UNINITIALIZED_BRIDGE_ERR
        scenes = self.bridge.get_scene() or {}
        return {id: scene for id, scene in scenes.items() if not scene.get('recycle')}

    @action
    def status(self, *_, **__) -> Iterable[LightEntity]:
        lights = self.transform_entities(self._get_lights(publish_entities=True))
        for light in lights:
            light.id = light.external_id
            for attr, value in (light.data or {}).items():
                setattr(light, attr, value)

            if light.external_id is not None:
                del light.external_id
            if light.data is not None:
                del light.data

        return lights

    def main(self):
        lights_prev = self._get_lights(publish_entities=True)  # Initialize the lights

        while not self.should_stop():
            try:
                lights_new = self._get_lights()
                for light_id, light in lights_new.items():
                    event_args = {}
                    new_state = light.get('state', {})
                    prev_state = lights_prev.get(light_id, {}).get('state', {})

                    for attr in ['on', 'bri', 'sat', 'hue', 'ct', 'xy']:
                        if attr in new_state and new_state.get(attr) != prev_state.get(
                            attr
                        ):
                            event_args[attr] = new_state.get(attr)

                    if event_args:
                        event_args['plugin_name'] = 'light.hue'
                        event_args['light_id'] = light_id
                        event_args['light_name'] = light.get('name')
                        get_bus().post(LightStatusChangeEvent(**event_args))
                        self.publish_entities([{'id': light_id, **light}])  # type: ignore

                lights_prev = lights_new
            finally:
                self.wait_stop(self.poll_interval)


# vim:sw=4:ts=4:et:
