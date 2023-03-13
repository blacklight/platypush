from .._base import BaseBluetoothClass, ClassProperty
from ._major import MajorDeviceClass


class MinorDeviceClass(BaseBluetoothClass):
    """
    Models Bluetooth minor device classes - see
    https://btprodspecificationrefs.blob.core.windows.net/assigned-numbers/Assigned%20Number%20Types/Assigned%20Numbers.pdf,
    Sections 2.8.2.1 - 2.8.2.9
    """

    # Computer classes
    COMPUTER_UNKNOWN = ClassProperty(
        'Unknown', 0xFC, 2, 0b000, MajorDeviceClass.COMPUTER
    )
    COMPUTER_DESKTOP = ClassProperty(
        'Desktop Workstation', 0xFC, 2, 0b001, MajorDeviceClass.COMPUTER
    )
    COMPUTER_SERVER = ClassProperty('Server', 0xFC, 2, 0b010, MajorDeviceClass.COMPUTER)
    COMPUTER_LAPTOP = ClassProperty('Laptop', 0xFC, 2, 0b011, MajorDeviceClass.COMPUTER)
    COMPUTER_HANDHELD_PDA = ClassProperty(
        'Handheld PDA', 0xFC, 2, 0b100, MajorDeviceClass.COMPUTER
    )
    COMPUTER_PALM_PDA = ClassProperty(
        'Palm-sized PDA', 0xFC, 2, 0b101, MajorDeviceClass.COMPUTER
    )
    COMPUTER_WEARABLE = ClassProperty(
        'Wearable Computer', 0xFC, 2, 0b110, MajorDeviceClass.COMPUTER
    )

    # Phone classes
    PHONE_UNKNOWN = ClassProperty('Unknown', 0xFC, 2, 0b000, MajorDeviceClass.PHONE)
    PHONE_CELLULAR = ClassProperty('Cellular', 0xFC, 2, 0b001, MajorDeviceClass.PHONE)
    PHONE_CORDLESS = ClassProperty('Cordless', 0xFC, 2, 0b010, MajorDeviceClass.PHONE)
    PHONE_SMARTPHONE = ClassProperty(
        'Smartphone', 0xFC, 2, 0b011, MajorDeviceClass.PHONE
    )
    PHONE_WIRED_MODEM = ClassProperty(
        'Wired Modem', 0xFC, 2, 0b100, MajorDeviceClass.PHONE
    )
    PHONE_ISDN_ACCESS = ClassProperty(
        'ISDN Access Point', 0xFC, 2, 0b101, MajorDeviceClass.PHONE
    )

    # LAN / Access Point classes
    AP_USAGE_0 = ClassProperty('Fully Available', 0xE0, 5, 0b000, MajorDeviceClass.AP)
    AP_USAGE_1_17 = ClassProperty(
        '1 - 17% Utilized', 0xE0, 5, 0b001, MajorDeviceClass.AP
    )
    AP_USAGE_17_33 = ClassProperty(
        '17 - 33% Utilized', 0xE0, 5, 0b010, MajorDeviceClass.AP
    )
    AP_USAGE_33_50 = ClassProperty(
        '33 - 50% Utilized', 0xE0, 5, 0b011, MajorDeviceClass.AP
    )
    AP_USAGE_50_67 = ClassProperty(
        '50 - 67% Utilized', 0xE0, 5, 0b100, MajorDeviceClass.AP
    )
    AP_USAGE_67_83 = ClassProperty(
        '67 - 83% Utilized', 0xE0, 5, 0b101, MajorDeviceClass.AP
    )
    AP_USAGE_83_99 = ClassProperty(
        '83 - 99% Utilized', 0xE0, 5, 0b110, MajorDeviceClass.AP
    )
    AP_USAGE_100 = ClassProperty(
        'No Service Available', 0xE0, 5, 0b111, MajorDeviceClass.AP
    )

    # Multimedia classes
    MULTIMEDIA_HEADSET = ClassProperty(
        'Headset', 0xFC, 2, 0b000001, MajorDeviceClass.MULTIMEDIA
    )
    MULTIMEDIA_HANDS_FREE = ClassProperty(
        'Hands-free Device', 0xFC, 2, 0b000010, MajorDeviceClass.MULTIMEDIA
    )
    MULTIMEDIA_MICROPHONE = ClassProperty(
        'Microphone', 0xFC, 2, 0b000100, MajorDeviceClass.MULTIMEDIA
    )
    MULTIMEDIA_LOUDSPEAKER = ClassProperty(
        'Loudspeaker', 0xFC, 2, 0b000101, MajorDeviceClass.MULTIMEDIA
    )
    MULTIMEDIA_HEADPHONES = ClassProperty(
        'Headphones', 0xFC, 2, 0b000110, MajorDeviceClass.MULTIMEDIA
    )
    MULTIMEDIA_PORTABLE_AUDIO = ClassProperty(
        'Portable Audio', 0xFC, 2, 0b000111, MajorDeviceClass.MULTIMEDIA
    )
    MULTIMEDIA_CAR_AUDIO = ClassProperty(
        'Car Audio', 0xFC, 2, 0b001000, MajorDeviceClass.MULTIMEDIA
    )
    MULTIMEDIA_SET_TOP_BOX = ClassProperty(
        'Set-top Box', 0xFC, 2, 0b001001, MajorDeviceClass.MULTIMEDIA
    )
    MULTIMEDIA_HIFI_AUDIO = ClassProperty(
        'HiFi Audio Device', 0xFC, 2, 0b001010, MajorDeviceClass.MULTIMEDIA
    )
    MULTIMEDIA_VCR = ClassProperty(
        'VCR', 0xFC, 2, 0b001011, MajorDeviceClass.MULTIMEDIA
    )
    MULTIMEDIA_VIDEO_CAMERA = ClassProperty(
        'Video Camera', 0xFC, 2, 0b001100, MajorDeviceClass.MULTIMEDIA
    )
    MULTIMEDIA_CAMCODER = ClassProperty(
        'Camcoder', 0xFC, 2, 0b001101, MajorDeviceClass.MULTIMEDIA
    )
    MULTIMEDIA_VIDEO_MONITOR = ClassProperty(
        'Video Monitor', 0xFC, 2, 0b001110, MajorDeviceClass.MULTIMEDIA
    )
    MULTIMEDIA_VIDEO_DISPLAY_AND_LOUDSPEAKER = ClassProperty(
        'Video Display and Loudspeaker', 0xFC, 2, 0b001111, MajorDeviceClass.MULTIMEDIA
    )
    MULTIMEDIA_VIDEO_CONFERENCING = ClassProperty(
        'Video Conferencing', 0xFC, 2, 0b010000, MajorDeviceClass.MULTIMEDIA
    )
    MULTIMEDIA_GAMING_TOY = ClassProperty(
        'Gaming / Toy', 0xFC, 2, 0b010010, MajorDeviceClass.MULTIMEDIA
    )

    # Peripheral classes
    PERIPHERAL_UNKNOWN = ClassProperty(
        'Unknown', 0xFC, 2, 0b000000, MajorDeviceClass.PERIPHERAL
    )
    PERIPHERAL_KEYBOARD = ClassProperty(
        'Keyboard', 0xC0, 6, 0b01, MajorDeviceClass.PERIPHERAL
    )
    PERIPHERAL_POINTER = ClassProperty(
        'Pointing Device', 0xC0, 6, 0b10, MajorDeviceClass.PERIPHERAL
    )
    PERIPHERAL_KEYBOARD_POINTER = ClassProperty(
        'Combo Keyboard/Pointing Device', 0xC0, 6, 0b11, MajorDeviceClass.PERIPHERAL
    )
    PERIPHERAL_JOYSTICK = ClassProperty(
        'Joystick', 0x3C, 2, 0b0001, MajorDeviceClass.PERIPHERAL
    )
    PERIPHERAL_GAMEPAD = ClassProperty(
        'Gamepad', 0x3C, 2, 0b0010, MajorDeviceClass.PERIPHERAL
    )
    PERIPHERAL_REMOTE_CONTROL = ClassProperty(
        'Remote Control', 0x3C, 2, 0b0011, MajorDeviceClass.PERIPHERAL
    )
    PERIPHERAL_SENSOR = ClassProperty(
        'Sensing Device', 0x3C, 2, 0b0100, MajorDeviceClass.PERIPHERAL
    )
    PERIPHERAL_DIGIT_TABLET = ClassProperty(
        'Digitizer Tablet', 0x3C, 2, 0b0101, MajorDeviceClass.PERIPHERAL
    )
    PERIPHERAL_CARD_READER = ClassProperty(
        'Card Reader', 0x3C, 2, 0b0110, MajorDeviceClass.PERIPHERAL
    )
    PERIPHERAL_DIGITAL_PEN = ClassProperty(
        'Card Reader', 0x3C, 2, 0b0111, MajorDeviceClass.PERIPHERAL
    )
    PERIPHERAL_SCANNER = ClassProperty(
        'Handheld Scanner', 0x3C, 2, 0b1000, MajorDeviceClass.PERIPHERAL
    )
    PERIPHERAL_GESTURES = ClassProperty(
        'Handheld Gesture Input Device', 0x3C, 2, 0b1001, MajorDeviceClass.PERIPHERAL
    )

    # Imaging classes
    IMAGING_UNKNOWN = ClassProperty(
        'Unknown', 0xFC, 2, 0b000000, MajorDeviceClass.IMAGING
    )
    IMAGING_DISPLAY = ClassProperty(
        'Display', 0xF0, 4, 0b0001, MajorDeviceClass.IMAGING
    )
    IMAGING_CAMERA = ClassProperty('Camera', 0xF0, 4, 0b0010, MajorDeviceClass.IMAGING)
    IMAGING_SCANNER = ClassProperty(
        'Scanner', 0xF0, 4, 0b0100, MajorDeviceClass.IMAGING
    )
    IMAGING_PRINTER = ClassProperty(
        'Printer', 0xF0, 4, 0b1000, MajorDeviceClass.IMAGING
    )

    # Wearable classes
    WEARABLE_UNKNOWN = ClassProperty(
        'Unknown', 0xFC, 2, 0b000000, MajorDeviceClass.WEARABLE
    )
    WEARABLE_WRISTWATCH = ClassProperty(
        'Wristwatch', 0xFC, 2, 0b000001, MajorDeviceClass.WEARABLE
    )
    WEARABLE_PAGER = ClassProperty(
        'Pager', 0xFC, 2, 0b000010, MajorDeviceClass.WEARABLE
    )
    WEARABLE_JACKET = ClassProperty(
        'Jacket', 0xFC, 2, 0b000011, MajorDeviceClass.WEARABLE
    )
    WEARABLE_HELMET = ClassProperty(
        'Helmet', 0xFC, 2, 0b000100, MajorDeviceClass.WEARABLE
    )
    WEARABLE_GLASSES = ClassProperty(
        'Glasses', 0xFC, 2, 0b000101, MajorDeviceClass.WEARABLE
    )

    # Toy classes
    TOY_UNKNOWN = ClassProperty('Unknown', 0xFC, 2, 0b000000, MajorDeviceClass.TOY)
    TOY_ROBOT = ClassProperty('Robot', 0xFC, 2, 0b000001, MajorDeviceClass.TOY)
    TOY_VEHICLE = ClassProperty('Vehicle', 0xFC, 2, 0b000010, MajorDeviceClass.TOY)
    TOY_DOLL = ClassProperty(
        'Doll / Action Figure', 0xFC, 2, 0b000011, MajorDeviceClass.TOY
    )
    TOY_CONTROLLER = ClassProperty(
        'Controller', 0xFC, 2, 0b000100, MajorDeviceClass.TOY
    )
    TOY_GAME = ClassProperty('Game', 0xFC, 2, 0b000101, MajorDeviceClass.TOY)

    # Health classes
    HEALTH_UNKNOWN = ClassProperty(
        'Unknown', 0xFC, 2, 0b000000, MajorDeviceClass.HEALTH
    )
    HEALTH_BLOOD_PRESSURE = ClassProperty(
        'Blood Pressure Monitor', 0xFC, 2, 0b000001, MajorDeviceClass.HEALTH
    )
    HEALTH_THERMOMETER = ClassProperty(
        'Thermometer', 0xFC, 2, 0b000010, MajorDeviceClass.HEALTH
    )
    HEALTH_SCALE = ClassProperty(
        'Weighing Scale', 0xFC, 2, 0b000011, MajorDeviceClass.HEALTH
    )
    HEALTH_GLUCOSE = ClassProperty(
        'Glucose Meter', 0xFC, 2, 0b000100, MajorDeviceClass.HEALTH
    )
    HEALTH_OXIMETER = ClassProperty(
        'Pulse Oximeter', 0xFC, 2, 0b000101, MajorDeviceClass.HEALTH
    )
    HEALTH_PULSE = ClassProperty(
        'Heart Rate/Pulse Monitor', 0xFC, 2, 0b000110, MajorDeviceClass.HEALTH
    )
    HEALTH_DISPLAY = ClassProperty(
        'Health Data Display', 0xFC, 2, 0b000111, MajorDeviceClass.HEALTH
    )
    HEALTH_STEPS = ClassProperty(
        'Step Counter', 0xFC, 2, 0b001000, MajorDeviceClass.HEALTH
    )
    HEALTH_COMPOSITION = ClassProperty(
        'Body Composition Analyzer', 0xFC, 2, 0b001001, MajorDeviceClass.HEALTH
    )
    HEALTH_PEAK_FLOW = ClassProperty(
        'Peak Flow Monitor', 0xFC, 2, 0b001010, MajorDeviceClass.HEALTH
    )
    HEALTH_MEDICATION = ClassProperty(
        'Medication Monitor', 0xFC, 2, 0b001011, MajorDeviceClass.HEALTH
    )
    HEALTH_KNEE_PROSTHESIS = ClassProperty(
        'Knee Prosthesis', 0xFC, 2, 0b001100, MajorDeviceClass.HEALTH
    )
    HEALTH_ANKLE_PROSTHESIS = ClassProperty(
        'Ankle Prosthesis', 0xFC, 2, 0b001101, MajorDeviceClass.HEALTH
    )
    HEALTH_GENERIC = ClassProperty(
        'Generic Health Manager', 0xFC, 2, 0b001110, MajorDeviceClass.HEALTH
    )
    HEALTH_MOBILITY = ClassProperty(
        'Personal Mobility Device', 0xFC, 2, 0b001111, MajorDeviceClass.HEALTH
    )
