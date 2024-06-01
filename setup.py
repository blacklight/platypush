#!/usr/bin/env python

import json
import os

from setuptools import setup, find_packages


def path(fname=''):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), fname))


def readfile(fname):
    with open(path(fname)) as f:
        return f.read()


def pkg_files(dir):
    paths = []
    for p, _, files in os.walk(dir):
        for file in files:
            paths.append(os.path.join('..', p, file))
    return paths


def scan_manifests():
    for root, _, files in os.walk('platypush'):
        for file in files:
            if file == 'manifest.json':
                yield os.path.join(root, file)


def parse_deps(deps):
    ret = []
    for dep in deps:
        if dep.startswith('git+'):
            continue  # Don't include git dependencies in the setup.py, or Twine will complain

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


plugins = pkg_files('platypush/plugins')
backend = pkg_files('platypush/backend')

setup(
    name="platypush",
    version="1.0.6",
    author="Fabio Manganiello",
    author_email="fabio@manganiello.tech",
    description="Platypush service",
    license="MIT",
    python_requires='>= 3.6',
    keywords="home-automation automation iot mqtt websockets redis dashboard notifications",
    url="https://platypush.tech",
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
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
    long_description=readfile('README.md'),
    long_description_content_type='text/markdown',
    classifiers=[
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
    ],
    install_requires=[
        'alembic',
        'croniter',
        'docutils',
        'flask',
        'frozendict',
        'marshmallow',
        'marshmallow_dataclass',
        'psutil',
        'python-dateutil',
        'python-magic',
        'pyyaml',
        'redis',
        'requests',
        'rsa',
        'sqlalchemy',
        'tornado',
        'websocket-client',
        'websockets',
        'wheel',
        'zeroconf>=0.27.0',
    ],
    extras_require=parse_manifests(),
)
