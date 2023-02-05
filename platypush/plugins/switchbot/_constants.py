from enum import Enum


class DeviceType(Enum):
    """
    Constants used for the `device_type` attribute.

    Reference: https://github.com/OpenWonderLabs/SwitchBotAPI
    """

    BLIND_TILT = 'Blind Tilt'
    BOT = 'Bot'
    CEILING_LIGHT = 'Ceiling Light'
    CEILING_LIGHT_PRO = 'Ceiling Light Pro'
    COLOR_BULB = 'Color Bulb'
    CONTACT_SENSOR = 'Contact Sensor'
    CURTAIN = 'Curtain'
    HUMIDIFIER = 'Humidifier'
    KEYPAD = 'Keypad'
    KEYPAD_TOUCH = 'Keypad Touch'
    LOCK = 'Smart Lock'
    METER = 'Meter'
    METER_PLUS = 'Meter Plus'
    MOTION_SENSOR = 'Motion Sensor'
    PLUG = 'Plug'
    PLUG_MINI_JP = 'Plug Mini (JP)'
    PLUG_MINI_US = 'Plug Mini (US)'
    ROBOT_VACUUM_CLEANER_S1 = 'Robot Vacuum Cleaner S1'
    ROBOT_VACUUM_CLEANER_S1_PLUS = 'Robot Vacuum Cleaner S1 Plus'
    STRIP_LIGHT = 'Strip Light'
