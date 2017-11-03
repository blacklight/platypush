#!/usr/bin/env python

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "runbullet",
    version = "0.1",
    author = "Fabio Manganiello",
    author_email = "info@fabiomanganiello.com",
    description = ("Runbullet service"),
    license = "BSD",
    keywords = "pushbullet notifications automation",
    url = "https://www.fabiomanganiello.com",
    packages=['runbullet'],
    long_description=read('README.md'),
    classifiers=[
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)

