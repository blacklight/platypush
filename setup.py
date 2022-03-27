#!/usr/bin/env python

import os
from setuptools import setup, find_packages


def path(fname=''):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), fname))


def readfile(fname):
    with open(path(fname)) as f:
        return f.read()


# noinspection PyShadowingBuiltins
def pkg_files(dir):
    paths = []
    # noinspection PyShadowingNames
    for (path, dirs, files) in os.walk(dir):
        for file in files:
            paths.append(os.path.join('..', path, file))
    return paths


plugins = pkg_files('platypush/plugins')
backend = pkg_files('platypush/backend')

setup(
    name="platypush",
    version="0.23.2",
    author="Fabio Manganiello",
    author_email="info@fabiomanganiello.com",
    description="Platypush service",
    license="MIT",
    python_requires='>= 3.6',
    keywords="home-automation automation iot mqtt websockets redis dashboard notifications",
    url="https://platypush.tech",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'platypush=platypush:main',
            'platydock=platypush.platydock:main',
        ],
    },
    scripts=['bin/platyvenv'],
    long_description=readfile('README.md'),
    long_description_content_type='text/markdown',
    classifiers=[
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
    ],
    install_requires=[
        'pyyaml',
        'redis',
        'requests',
        'croniter',
        'sqlalchemy',
        'websockets',
        'websocket-client',
        'wheel',
        'zeroconf>=0.27.0',
        'tz',
        'python-dateutil',
        'cryptography',
        'pyjwt',
        'marshmallow',
        'frozendict',
    ],

    extras_require={
        # Support for thread custom name
        'threadname': ['python-prctl'],
        # Support for Kafka backend and plugin
        'kafka': ['kafka-python'],
        # Support for Pushbullet backend and plugin
        'pushbullet': ['pushbullet.py @ https://github.com/rbrcsk/pushbullet.py/tarball/master'],
        # Support for HTTP backend
        'http': ['flask', 'bcrypt', 'python-magic', 'gunicorn'],
        # Support for MQTT backends
        'mqtt': ['paho-mqtt'],
        # Support for RSS feeds parser
        'rss': ['feedparser'],
        # Support for PDF generation
        'pdf': ['weasyprint'],
        # Support for Philips Hue plugin
        'hue': ['phue'],
        # Support for MPD/Mopidy music server plugin and backend
        'mpd': ['python-mpd2'],
        # Support for Google text2speech plugin
        'google-tts': ['oauth2client', 'google-api-python-client', 'google-cloud-texttospeech'],
        # Support for OMXPlayer plugin
        'omxplayer': ['omxplayer-wrapper'],
        # Support for YouTube
        'youtube': ['youtube-dl'],
        # Support for torrents download
        'torrent': ['python-libtorrent-bin'],
        # Generic support for cameras
        'camera': ['numpy', 'Pillow'],
        # Support for RaspberryPi camera
        'picamera': ['picamera', 'numpy', 'Pillow'],
        # Support for inotify file monitors
        'inotify': ['inotify'],
        # Support for Google Assistant
        'google-assistant-legacy': ['google-assistant-library'],
        'google-assistant': ['google-assistant-sdk[samples]'],
        # Support for the Google APIs
        'google': ['oauth2client', 'google-api-python-client'],
        # Support for Last.FM scrobbler plugin
        'lastfm': ['pylast'],
        # Support for custom hotword detection
        'hotword': ['snowboy'],
        'snowboy': ['snowboy'],
        # Support for real-time MIDI events
        'midi': ['rtmidi'],
        # Support for RaspberryPi GPIO
        'rpi-gpio': ['RPi.GPIO'],
        # Support for MCP3008 analog-to-digital converter plugin
        'mcp3008': ['adafruit-mcp3008'],
        # Support for smart cards detection
        'scard': ['pyscard'],
        # Support for serial port plugin
        'serial': ['pyserial'],
        # Support for ICal calendars
        'ical': ['icalendar'],
        # Support for joystick backend
        'joystick': ['inputs'],
        # Support for Kodi plugin
        'kodi': ['kodi-json'],
        # Support for Plex plugin
        'plex': ['plexapi'],
        # Support for Chromecast plugin
        'chromecast': ['pychromecast'],
        # Support for sound devices
        'sound': ['sounddevice', 'soundfile', 'numpy'],
        # Support for web media subtitles
        'subtitles': [
            'webvtt-py',
            'python-opensubtitles @ https://github.com/agonzalezro/python-opensubtitles/tarball/master'],
        # Support for mpv player plugin
        'mpv': ['python-mpv'],
        # Support for NFC tags
        'nfc': ['nfcpy>=1.0', 'ndeflib'],
        # Support for enviropHAT
        'envirophat': ['envirophat'],
        # Support for GPS
        'gps': ['gps'],
        # Support for BME280 environment sensor
        'bme280': ['pimoroni-bme280'],
        # Support for LTR559 light/proximity sensor
        'ltr559': ['ltr559'],
        # Support for VL53L1X laser ranger/distance sensor
        'vl53l1x': ['smbus2', 'vl53l1x'],
        # Support for Dropbox integration
        'dropbox': ['dropbox'],
        # Support for Leap Motion backend
        'leap': ['leap-sdk @ https://github.com/BlackLight/leap-sdk-python3/tarball/master'],
        # Support for Flic buttons
        'flic': ['flic @ https://github.com/50ButtonsEach/fliclib-linux-hci/tarball/master'],
        # Support for Alexa/Echo plugin
        'alexa': ['avs @ https://github.com/BlackLight/avs/tarball/master'],
        # Support for bluetooth devices
        'bluetooth': ['pybluez', 'gattlib',
                      'pyobex @ https://github.com/BlackLight/PyOBEX/tarball/master'],
        # Support for TP-Link devices
        'tplink': ['pyHS100'],
        # Support for PMW3901 2-Dimensional Optical Flow Sensor
        'pmw3901': ['pmw3901'],
        # Support for MLX90640 thermal camera
        'mlx90640': ['Pillow'],
        # Support for machine learning models and cameras over OpenCV
        'cv': ['opencv-python', 'numpy', 'Pillow'],
        # Support for the generation of HTML documentation from docstring
        'htmldoc': ['docutils'],
        # Support for Node-RED integration
        'nodered': ['pynodered'],
        # Support for Todoist integration
        'todoist': ['todoist-python'],
        # Support for Trello integration
        'trello': ['py-trello'],
        # Support for Google Pub/Sub
        'google-pubsub': ['google-cloud-pubsub'],
        # Support for Google Translate
        'google-translate': ['google-cloud-translate'],
        # Support for keyboard/mouse plugin
        'inputs': ['pyuserinput'],
        # Support for Buienradar weather forecast
        'buienradar': ['buienradar'],
        # Support for Telegram integration
        'telegram': ['python-telegram-bot'],
        # Support for Arduino integration
        'arduino': ['pyserial', 'pyfirmata2'],
        # Support for CUPS printers management
        'cups': ['pycups'],
        # Support for Graphite integration
        'graphite': ['graphyte'],
        # Support for CPU and memory monitoring and info
        'sys': ['py-cpuinfo', 'psutil'],
        # Support for nmap integration
        'nmap': ['python-nmap'],
        # Support for zigbee2mqtt
        'zigbee': ['paho-mqtt'],
        # Support for Z-Wave
        'zwave': ['python-openzwave'],
        # Support for Mozilla DeepSpeech speech-to-text engine
        'deepspeech': ['deepspeech', 'numpy', 'sounddevice'],
        # Support for PicoVoice hotword detection engine
        'picovoice-hotword': ['pvporcupine'],
        # Support for PicoVoice speech-to-text engine
        'picovoice-speech': ['pvcheetah @ git+https://github.com/BlackLight/cheetah'],
        # Support for OTP (One-Time Password) generation
        'otp': ['pyotp'],
        # Support for Linode integration
        'linode': ['linode_api4'],
        # Support for QR codes
        'qrcode': ['numpy', 'qrcode[pil]', 'Pillow', 'pyzbar'],
        # Support for Tensorflow
        'tensorflow': ['numpy', 'tensorflow>=2.0', 'keras', 'pandas'],
        # Support for Samsung TizenOS-based smart TVs
        'samsungtv': ['samsungtvws'],
        # Support for SSH integration
        'ssh': ['paramiko'],
        # Support for clipboard integration
        'clipboard': ['pyperclip'],
        # Support for luma.oled display drivers
        'luma-oled': ['luma.oled @ git+https://github.com/rm-hull/luma.oled'],
        # Support for DBus integration
        'dbus': ['pydbus', 'defusedxml'],
        # Support for Twilio integration
        'twilio': ['twilio'],
        # Support for DHT11/DHT22/AM2302 temperature/humidity sensors
        'dht': ['Adafruit_Python_DHT @ git+https://github.com/adafruit/Adafruit_Python_DHT'],
        # Support for LCD display integration
        'lcd': ['RPi.GPIO', 'RPLCD'],
        # Support for IMAP mail integration
        'imap': ['imapclient'],
        # Support for NextCloud integration
        'nextcloud': ['nextcloud-api-wrapper'],
        # Support for VLC integration
        'vlc': ['python-vlc'],
        # Support for SmartThings integration
        'smartthings': ['pysmartthings', 'aiohttp'],
        # Support for file.monitor backend
        'filemonitor': ['watchdog'],
        # Support for Adafruit PCA9685 PWM controller
        'pca9685': ['adafruit-python-shell', 'adafruit-circuitpython-pca9685'],
        # Support for ngrok integration
        'ngrok': ['pyngrok'],
        # Support for IRC integration
        'irc': ['irc'],
    },
)
