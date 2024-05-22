#!/bin/sh

# Install git
if [ -z "$(which git)" ]; then
  if [ -n "$(which apt-get)" ]; then
    apt-get update
    apt-get install -y git
  elif [ -n "$(which apk)" ]; then
    apk add --update --no-cache git
  elif [ -n "$(which yum)" ]; then
    yum install -y git
  elif [ -n "$(which dnf)" ]; then
    dnf install -y git
  elif [ -n "$(which pacman)" ]; then
    pacman -Sy --noconfirm git
  else
    echo "Could not find a package manager to install git"
    exit 1
  fi
fi

# Backup the original git configuration before changing attributes
export GIT_CONF="$PWD/.git/config"
export TMP_GIT_CONF=/tmp/git.config.orig
cp "$GIT_CONF" "$TMP_GIT_CONF"

git config --global --add safe.directory "$PWD"
git config user.name "Platypush CI/CD Automation"
git config user.email "admin@platypush.tech"
