#!/bin/sh

apk add --update --no-cache $(cat platypush/install/requirements/alpine.txt) py3-cryptography openssl
pip install . --break-system-packages
pip install -r requirements-tests.txt --break-system-packages
pytest tests
