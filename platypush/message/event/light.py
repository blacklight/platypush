from typing import Optional

from platypush.message.event import Event


class LightEvent(Event):
    """
    Base class for light plugins events.
    """
    def __init__(self, *args, plugin_name: Optional[str] = None, **kwargs):
        """
        :param plugin_name: Name of the :class:`platypush.plugins.light.LightPlugin` instance that triggered the event.
        """
        super().__init__(*args, plugin_name=plugin_name, **kwargs)


class LightStatusChangeEvent(LightEvent):
    """
    Event triggered when the state of a lightbulb changes
    """
    def __init__(self, light_id=None, light_name=None, on=None, bri=None,
                 sat=None, hue=None, ct=None, xy=None, *args, **kwargs):
        """
        :param light_id: Light ID that triggered the event
        :type light_id: int

        :param light_name: Light name that triggered the event
        :type light_name: str

        :param on: Set if the power state of the bulb changed
        :type on: bool

        :param bri: Set if the brightness state of the bulb changed
        :type bri: int

        :param sat: Set if the saturation state of the bulb changed
        :type sat: int

        :param hue: Set if the hue state of the bulb changed
        :type hue: int

        :param ct: Set if the color temperature state of the bulb changed
        :type ct: int

        :param xy: Set if the color of the bulb (expressed in XY coordinates) has changed
        :type xy: list
        """

        attrs = {}

        if light_id is not None:
            attrs['light_id'] = light_id
        if light_name is not None:
            attrs['light_name'] = light_name
        if on is not None:
            attrs['on'] = on
        if bri is not None:
            attrs['bri'] = bri
        if sat is not None:
            attrs['sat'] = sat
        if hue is not None:
            attrs['hue'] = hue
        if ct is not None:
            attrs['ct'] = ct
        if xy is not None:
            attrs['xy'] = xy

        super().__init__(*args, **attrs, **kwargs)


class LightAnimationStartedEvent(LightEvent):
    """
    Event triggered when a light animation is started.
    """
    def __init__(self, *args, animation, lights: Optional[list] = None, groups: Optional[list] = None, **kwargs):
        super().__init__(*args, animation=animation, lights=lights, groups=groups, **kwargs)


class LightAnimationStoppedEvent(LightEvent):
    """
    Event triggered when a light animation is stopped.
    """
    def __init__(self, *args, animation=None, lights: Optional[list] = None, groups: Optional[list] = None, **kwargs):
        super().__init__(*args, animation=animation, lights=lights, groups=groups, **kwargs)


# vim:sw=4:ts=4:et:
