#!/bin/sh

apk add --update --no-cache --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing/ $(cat platypush/install/requirements/alpine.txt)
pip install . --break-system-packages
pip install -r requirements-tests.txt --break-system-packages
pytest tests
