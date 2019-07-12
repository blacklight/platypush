#!/usr/bin/env python

import errno
import os
import re
import distutils.cmd
from distutils.command.build import build
from setuptools import setup, find_packages


class WebBuildCommand(distutils.cmd.Command):
    """
    Custom command to build the web files
    """

    description = 'Build components and styles for the web pages'
    user_options = []

    @classmethod
    def generate_css_files(cls):
        from scss import Compiler

        print('Building CSS files')
        base_path = path(os.path.join('platypush','backend','http','static','css'))
        input_path = path(os.path.join(base_path,'source'))
        output_path = path(os.path.join(base_path,'dist'))

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



class BuildCommand(build):
    def run(self):
        build.run(self)
        self.run_command('web_build')


def path(fname=''):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), fname))


def readfile(fname):
    with open(path(fname)) as f:
        return f.read()


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
    version = "0.10.4",
    author = "Fabio Manganiello",
    author_email = "info@fabiomanganiello.com",
    description = ("Platypush service"),
    license = "MIT",
    python_requires = '>= 3.5',
    keywords = "home-automation iot mqtt websockets redis dashboard notificaions",
    url = "https://github.com/BlackLight/platypush",
    packages = find_packages(),
    include_package_data = True,
    entry_points = {
        'console_scripts': [
            'platypush=platypush:main',
            'pusher=platypush.pusher:main',
            'platydock=platypush.platydock:main',
        ],
    },
    scripts = ['bin/platyvenv'],
    cmdclass = {
        'web_build': WebBuildCommand,
        'build': BuildCommand,
    },
    # data_files = [
    #     ('/etc/platypush', ['platypush/config.example.yaml'])
    # ],
    long_description = readfile('README.md'),
    long_description_content_type = 'text/markdown',
    classifiers = [
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
    ],
    install_requires = [
        'pyyaml',
        'redis',
        'requests',
    ],
    extras_require = {
        'Support for custom thread and process names': ['python-prctl'],
        'Support for Apache Kafka backend': ['kafka-python'],
        'Support for Pushbullet backend': ['requests', 'pushbullet.py'],
        'Support for HTTP backend': ['flask','websockets', 'python-dateutil'],
        'Support for HTTP poll backend': ['frozendict'],
        'Support for external web server': ['uwsgi'],
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
        'Support for joystick backend': ['inputs'],
        'Support for Kodi plugin': ['kodi-json'],
        'Support for Plex plugin': ['plexapi'],
        'Support for Chromecast plugin': ['pychromecast'],
        'Support for sound devices': ['sounddevice', 'soundfile', 'numpy'],
        'Support for web media subtitles': ['webvtt-py'],
        'Support for mopidy backend': ['websocket-client'],
        'Support for mpv player plugin': ['python-mpv'],
        'Support for compiling SASS/SCSS styles to CSS': ['pyScss'],
        'Support for NFC tags': ['nfcpy>=1.0', 'ndef'],
        # 'Support for Leap Motion backend': ['git+ssh://git@github.com:BlackLight/leap-sdk-python3.git'],
        # 'Support for Flic buttons': ['git+https://@github.com/50ButtonsEach/fliclib-linux-hci.git']
        # 'Support for media subtitles': ['git+https://github.com/agonzalezro/python-opensubtitles#egg=python-opensubtitles']
    },
)

