#!/bin/sh

apk add --update --no-cache py3-twine
python setup.py sdist bdist_wheel
twine upload dist/platypush-$(python setup.py --version).tar.gz
