#!/bin/sh

[ -f .skipci ] && exit 0

apk add --update --no-cache curl pacman sudo

. .drone/macros/configure-ssh.sh
. .drone/macros/configure-git.sh

git pull --rebase origin master --tags

export VERSION=$(python setup.py --version)
export HEAD=$(git log --pretty=format:%h HEAD...HEAD~1 | head -1)
export GIT_VERSION="$VERSION.r$(git log --pretty=oneline HEAD...v$VERSION | wc -l).g${HEAD}"

ssh-keyscan aur.archlinux.org >> ~/.ssh/known_hosts 2>/dev/null
adduser -u 1000 -D build
mkdir -p "$WORKDIR"

echo "--- Updating Arch git version"
export PKGDIR=$WORKDIR/git
git clone ssh://aur@aur.archlinux.org/platypush-git.git "$PKGDIR"
git config --global --add safe.directory "$PKGDIR"
chown -R build "$PKGDIR"
cd "$PKGDIR"

sed -i 'PKGBUILD' -r \
  -e "s/^pkgver=.*/pkgver=$GIT_VERSION/" \
  -e "s/^pkgrel=.*/pkgrel=1/" \

sudo -u build makepkg --printsrcinfo > .SRCINFO
export FILES_CHANGED=$(git status --porcelain --untracked-files=no | wc -l)

if [ $FILES_CHANGED -gt 0 ]; then
  echo "--- Pushing git package version $GIT_VERSION"
  git commit -a -m '[Automatic] Package update'
  git push origin master
fi
