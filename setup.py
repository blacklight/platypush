#!/usr/bin/env python

import errno
import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def pkg_files(dir):
    paths = []
    for (path, dirs, files) in os.walk(dir):
        for file in files:
            paths.append(os.path.join('..', path, file))
    return paths

def create_etc_dir():
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
    name = "platypush",
    version = "0.9",
    author = "Fabio Manganiello",
    author_email = "info@fabiomanganiello.com",
    description = ("Platypush service"),
    license = "MIT",
    python_requires = '>= 3',
    keywords = "pushbullet notifications automation",
    url = "https://github.com/BlackLight/platypush",
    packages = find_packages(),
    include_package_data = True,
    entry_points = {
        'console_scripts': [
            'platypush=platypush:main',
            'pusher=platypush.pusher:main',
        ],
    },
    # data_files = [
    #     ('/etc/platypush', ['platypush/config.example.yaml'])
    # ],
    long_description = read('README.md'),
    classifiers = [
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
    ],
    install_requires = [
        'pyyaml',
        'requires',
        'redis',
    ],
    extras_require = {
        'Support for Apache Kafka backend': ['kafka-python'],
        'Support for Pushbullet backend': ['requests', 'websocket-client'],
        'Support for HTTP backend': ['flask','websockets'],
        'Support for HTTP poll backend': ['frozendict'],
        'Support for database plugin': ['sqlalchemy'],
        'Support for RSS feeds': ['feedparser'],
        'Support for PDF generation': ['weasyprint'],
        'Support for Philips Hue plugin': ['phue'],
        'Support for MPD/Mopidy music server plugin': ['python-mpd2'],
        'Support for Belkin WeMo Switch plugin': ['ouimeaux'],
        'Support for text2speech plugin': ['mplayer'],
        'Support for OMXPlayer plugin': ['omxplayer'],
        'Support for YouTube in the OMXPlayer plugin': ['youtube-dl'],
        'Support for torrents download': ['python-libtorrent'],
        'Support for Google Assistant': ['google-assistant-library'],
        'Support for the Google APIs': ['google-api-python-client'],
        'Support for most of the HTTP poll backends': ['python-dateutil'],
        'Support for Last.FM scrobbler plugin': ['pylast'],
        'Support for custom hotword detection': ['snowboy'],
        'Support for real-time MIDI events': ['rtmidi'],
        'Support for GPIO pins access': ['RPi.GPIO'],
        'Support for MCP3008 analog-to-digital converter plugin': ['adafruit-mcp3008'],
        'Support for smart cards detection': ['pyscard'],
        'Support for ICal calendars': ['icalendar', 'python-dateutil'],
        # 'Support for Leap Motion backend': ['git+ssh://git@github.com:BlackLight/leap-sdk-python3.git'],
        # 'Support for Flic buttons': ['git+ssh://git@github.com/50ButtonsEach/fliclib-linux-hci']
    },
)

