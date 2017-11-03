#!/usr/bin/env python

import errno
import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def pkg_files(dir):
    paths = []
    for (path, dirs, files) in os.walk(dir):
        for file in files:
            paths.append(os.path.join('..', path, file))
    return paths

def create_etc_dir():
    path = '/etc/runbullet'
    try:
        os.makedirs(path)
    except OSError as e:
        if isinstance(e, PermissionError) \
                or e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

plugins = pkg_files('runbullet/plugins')
create_etc_dir()

setup(
    name = "runbullet",
    version = "0.2.0.dev1",
    author = "Fabio Manganiello",
    author_email = "info@fabiomanganiello.com",
    description = ("Runbullet service"),
    license = "MIT",
    python_requires = '>= 3',
    keywords = "pushbullet notifications automation",
    url = "https://github.com/BlackLight/runbullet",
    packages = ['runbullet'],
    package_data = {'': plugins},
    scripts = ['runbullet/bin/pusher'],
    entry_points = {
        'console_scripts': [
            'runbullet=runbullet:main',
        ],
    },
    data_files = [
        ('/etc/runbullet', ['runbullet/config.example.yaml'])
    ],
    long_description = read('README.md'),
    classifiers = [
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
    ],
    install_requires = [
        'pyyaml'
    ],
)

