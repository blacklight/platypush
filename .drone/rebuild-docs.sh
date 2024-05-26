#!/bin/sh

echo "Installing required build dependencies"
apk add --update --no-cache git make py3-sphinx py3-myst-parser py3-pip $(cat platypush/install/requirements/alpine.txt)
pip install -U sphinx-rtd-theme sphinx-book-theme --break-system-packages
pip install . --break-system-packages
mkdir -p /docs/current
export APPDIR="$PWD"
rm -rf "$APPDIR/docs/build"

echo "Building the updated documentation"
cd "$APPDIR/docs/source"
git clone 'https://git.platypush.tech/platypush/platypush.wiki.git' wiki

echo "Linking the wiki to the Sphinx index"
cd wiki
cd "$APPDIR/docs"
make html
rm -f config*.yaml
cd "$APPDIR"

echo "Copying the new documentation files to the target folder"
mv -v "$APPDIR/docs/build" /docs/new
cd /docs
mv current old
mv new current
rm -rf old
