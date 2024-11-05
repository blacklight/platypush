#!/usr/bin/env python

import json
import os

from setuptools import setup, find_packages


def path(fname=''):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), fname))


def readfile(fname):
    with open(path(fname)) as f:
        return f.read()


def scan_manifests():
    for root, _, files in os.walk('platypush'):
        for file in files:
            if file == 'manifest.json':
                yield os.path.join(root, file)


def parse_deps(deps):
    ret = []
    for dep in deps:
        if dep.startswith('git+'):
            continue  # Don't include git dependencies in pip, or Twine will complain

        ret.append(dep)

    return ret


def parse_manifest(manifest_file):
    with open(manifest_file) as f:
        manifest = json.load(f).get('manifest')
        if not manifest:
            return None, None

        name = '.'.join(manifest['package'].split('.')[2:])
        return name, parse_deps(manifest.get('install', {}).get('pip', []))


def parse_manifests():
    ret = {}
    for manifest_file in scan_manifests():
        name, deps = parse_manifest(manifest_file)
        if deps:
            ret[name] = deps

    return ret


setup(
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    extras_require=parse_manifests(),
    package_data={
        'platypush': [
            'migrations/alembic.ini',
            'migrations/alembic/*',
            'migrations/alembic/**/*',
            'install/**',
            'install/scripts/*',
            'install/scripts/**/*',
            'install/requirements/*',
            'install/docker/*',
            'components.json.gz',
        ],
    },
    entry_points={
        'console_scripts': [
            'platypush=platypush:main',
            'platydock=platypush.platydock:main',
            'platyvenv=platypush.platyvenv:main',
        ],
    },
    install_requires=[
        line.split('#')[0].strip()
        for line in readfile('requirements.txt').splitlines()
        if line.strip().split('#')[0].strip()
    ],
)
