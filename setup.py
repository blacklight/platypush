#!/usr/bin/env python

import errno
import os
import re
from distutils.cmd import Command
from distutils.command.build import build as _build
from distutils.command.install import install as _install
from setuptools.command.bdist_egg import bdist_egg as _bdist_egg
from setuptools import setup, find_packages


class WebBuildCommand(Command):
    """
    Custom command to build the web files
    """

    description = 'Build components and styles for the web pages'
    user_options = []

    @classmethod
    def generate_css_files(cls):
        try:
            # noinspection PyPackageRequirements
            from scss import Compiler
        except ImportError:
            print('pyScss module not found: {}. You will have to generate ' +
                  'the CSS files manually through python setup.py build install')
            return

        print('Building CSS files')
        base_path = path(os.path.join('platypush', 'backend', 'http', 'static', 'css'))
        input_path = path(os.path.join(base_path, 'source'))
        output_path = path(os.path.join(base_path, 'dist'))

        for root, dirs, files in os.walk(input_path, followlinks=True):
            scss_file = os.path.join(root, 'index.scss')
            if os.path.isfile(scss_file):
                css_path = os.path.split(scss_file[len(input_path):])[0][1:] + '.css'
                css_dir = os.path.join(output_path, os.path.dirname(css_path))
                css_file = os.path.join(css_dir, os.path.basename(css_path))

                os.makedirs(css_dir, exist_ok=True)
                print('\tGenerating CSS {scss} -> {css}'.format(scss=scss_file, css=css_file))

                with open(css_file, 'w') as f:
                    css_content = Compiler(output_style='compressed', search_path=[root, input_path]).compile(scss_file)
                    css_content = cls._fix_css4_vars(css_content)
                    f.write(css_content)

    @staticmethod
    def _fix_css4_vars(css):
        return re.sub(r'var\("--([^"]+)"\)', r'var(--\1)', css)

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.generate_css_files()


class install(_install):
    def do_egg_install(self):
        self.run_command('web_build')
        _install.do_egg_install(self)


class bdist_egg(_bdist_egg):
    def run(self):
        self.run_command('web_build')
        _bdist_egg.run(self)


class build(_build):
    sub_commands = _build.sub_commands + [('web_build', None)]


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


def create_etc_dir():
    # noinspection PyShadowingNames
    path = '/etc/platypush'
    try:
        os.makedirs(path)
    except OSError as e:
        if isinstance(e, PermissionError):
            print('WARNING: Could not create /etc/platypush')
        elif e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


plugins = pkg_files('platypush/plugins')
backend = pkg_files('platypush/backend')
# create_etc_dir()

setup(
    name="platypush",
    version="0.13.8",
    author="Fabio Manganiello",
    author_email="info@fabiomanganiello.com",
    description="Platypush service",
    license="MIT",
    python_requires='>= 3.6',
    keywords="home-automation iot mqtt websockets redis dashboard notificaions",
    url="https://github.com/BlackLight/platypush",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'platypush=platypush:main',
            'pusher=platypush.pusher:main',
            'platydock=platypush.platydock:main',
        ],
    },
    scripts=['bin/platyvenv'],
    cmdclass={
        'web_build': WebBuildCommand,
        'install': install,
        'build': build,
        'bdist_egg': bdist_egg,
    },
    # data_files = [
    #     ('/etc/platypush', ['platypush/config.example.yaml'])
    # ],
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
        'pyScss',
        'sqlalchemy',
        'websockets',
        'websocket-client',
        'wheel',
        'zeroconf>=0.27.0',
        'tz',
    ],

    extras_require={
        # Support for thread custom name
        'threadname': ['python-prctl'],
        # Support for Kafka backend and plugin
        'kafka': ['kafka-python'],
        # Support for Pushbullet backend and plugin
        'pushbullet': ['pushbullet.py @ https://github.com/rbrcsk/pushbullet.py/tarball/master'],
        # Support for HTTP backend
        'http': ['flask', 'python-dateutil', 'frozendict', 'bcrypt'],
        # Support for uWSGI HTTP backend
        'uwsgi': ['flask', 'python-dateutil', 'frozendict', 'uwsgi', 'bcrypt'],
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
        'torrent': ['python-libtorrent'],
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
        'ical': ['icalendar', 'python-dateutil'],
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
        'alexa': ['avs @ https://github.com:BlackLight/avs/tarball/master'],
        # Support for bluetooth devices
        'bluetooth': ['pybluez', 'gattlib',
                      'pyobex @ https://github.com/BlackLight/PyOBEX/tarball/master'],
        # Support for TP-Link devices
        'tplink': ['pyHS100'],
        # Support for PWM3901 2-Dimensional Optical Flow Sensor
        'pwm3901': ['pwm3901'],
        # Support for MLX90640 thermal camera
        'mlx90640': ['Pillow'],
        # Support for machine learning models and cameras over OpenCV
        'cv': ['cv2', 'numpy', 'Pillow'],
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
        'deepspeech': ['deepspeech', 'numpy','sounddevice'],
        # Support for PicoVoice hotword detection engine
        'picovoice-hotword': ['pvporcupine'],
        # Support for PicoVoice speech-to-text engine
        'picovoice-speech': ['pvcheetah @ git+https://github.com/BlackLight/cheetah'],
        # Support for OTP (One-Time Password) generation
        'otp': ['pyotp'],
        # Support for Linode integration
        'linode': ['linode_api4'],
        # Support for QR codes
        'qrcode': ['numpy','qrcode[pil]', 'Pillow', 'pyzbar'],
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
        'dbus': ['dbus-python'],
        # Support for Twilio integration
        'twilio': ['twilio'],
        # Support for Github integration
        'github': ['pytz'],
        # Support for DHT11/DHT22/AM2302 temperature/humidity sensors
        'dht': ['Adafruit_Python_DHT @ git+https://github.com/adafruit/Adafruit_Python_DHT'],
        # Support for LCD display integration
        'lcd': ['RPi.GPIO', 'RPLCD'],
        # Support for IMAP mail integration
        'imap': ['imapclient'],
        # Support for NextCloud integration
        'nextcloud': ['nextcloud-API @ git+https://github.com/EnterpriseyIntranet/nextcloud-API.git'],
        # Support for GStreamer integration
        'gstreamer': ['gst-python'],
    },
)
