#!/bin/sh

apk add --update --no-cache py3-twine py3-setuptools py3-wheel py3-pip
python setup.py sdist bdist_wheel
twine upload dist/platypush-$(python setup.py --version).tar.gz
