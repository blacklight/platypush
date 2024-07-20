#!/bin/sh

[ -f .skipci ] && exit 0

apk add --update --no-cache curl pacman sudo

. .drone/macros/configure-ssh.sh
. .drone/macros/configure-git.sh

git pull --rebase origin master --tags

export VERSION=$(python setup.py --version)
export TAG_URL="https://git.platypush.tech/platypush/platypush/archive/v$VERSION.tar.gz"

ssh-keyscan aur.archlinux.org >> ~/.ssh/known_hosts 2>/dev/null
adduser -u 1000 -D build
mkdir -p "$WORKDIR"

echo "--- Updating Arch stable version"
export PKGDIR="$WORKDIR/stable"
git clone ssh://aur@aur.archlinux.org/platypush.git "$PKGDIR"
git config --global --add safe.directory "$PKGDIR"
chown -R build "$PKGDIR"
cd "$PKGDIR"
export RELEASED_VERSION=$(grep -e '^pkgver=' PKGBUILD | sed -r -e 's/^pkgver=(.*)\s*/\1/')

if [ "$RELEASED_VERSION" == "$VERSION" ]; then
  echo "--- No changes in the stable package version"
  exit 0
fi

export TAG_CHECKSUM=$(curl --silent "$TAG_URL" | sha512sum | awk '{print $1}')

sed -i 'PKGBUILD' -r \
  -e "s/^pkgver=.*/pkgver=$VERSION/" \
  -e "s/^pkgrel=.*/pkgrel=1/" \
  -e "s/^sha512sums=.*/sha512sums=('$TAG_CHECKSUM')/"

sudo -u build makepkg --printsrcinfo > .SRCINFO
export FILES_CHANGED=$(git status --porcelain --untracked-files=no | wc -l)

if [ $FILES_CHANGED -gt 0 ]; then
  echo "--- Pushing stable package version $VERSION"
  git commit -a -m '[Automatic] Package update'
  git push origin master
fi
