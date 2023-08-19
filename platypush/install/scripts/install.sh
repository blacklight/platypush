#!/bin/sh

# This script parses the system requirements for a specific OS and it runs the
# appropriate package manager command to install them.

# This script is usually symlinked in the folders of the individual operating
# systems, and it's not supposed to be invoked directly.
# Instead, it will be called either by the root install.sh script or by a
# Dockerfile.

SCRIPT_PATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
OS="$(basename "$SCRIPT_PATH")"
CMD="$(cat "${SCRIPT_PATH}/PKGCMD")"
REQUIREMENTS="$(cat "${SCRIPT_PATH}/../../requirements/${OS}.txt" | tr '\n' ' ')"
SUDO=

# If we are running in a Docker context then we want to copy the docker-run.sh
# script where we can easily find it.
if [ -n "$DOCKER_CTX" ]; then
  cp -v /install/platypush/install/scripts/docker-run.sh /run.sh
fi

# If we aren't running in a Docker context, or the user is not root, we should
# use sudo to install system packages.
if [[ "$(id -u)" != "0" ]] || [ -z "$DOCKER_CTX" ]; then
  if ! type sudo >/dev/null; then
    echo "sudo executable not found, I can't install system packages" >&2
    exit 1
  fi

  SUDO="sudo"
fi

${SUDO_ARGS} ${CMD} ${REQUIREMENTS}
