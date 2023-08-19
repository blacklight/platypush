#!/bin/sh

# This script is used as a default entry point for Docker containers

DOCKER_CTX=1 platypush \
  --start-redis \
  --config /etc/platypush/config.yaml \
  --workdir /var/lib/platypush
