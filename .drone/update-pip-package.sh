#!/bin/sh

apk add --update --no-cache py3-twine py3-setuptools py3-wheel py3-pip py3-build
rm -rf build
python -m build
twine upload dist/platypush-$(python setup.py --version).tar.gz
