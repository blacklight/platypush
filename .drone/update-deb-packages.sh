#!/bin/sh

[ -f .skipci ] && exit 0

echo "-- Copying source directory"
mkdir -p "$WORKDIR/src"
export SRCDIR="$WORKDIR/src/$DEB_VERSION"
cp -r "$PWD" "$SRCDIR"
cd "$SRCDIR"

echo "-- Installing dependencies"
export DEBIAN_FRONTEND=noninteractive
apt update
apt install -y curl dpkg-dev gpg git python3 python3-pip python3-setuptools

echo "--- Parsing metadata"
git config --global --add safe.directory "$PWD"
git pull --rebase origin master --tags
export VERSION=$(grep -e '^__version__' "${SRCDIR}/version.py" | sed -r -e 's/^__version__\s*=\s*"([^"]+)"$/\1/')
export GIT_VERSION="$VERSION-$(git log --pretty=oneline HEAD...v$VERSION | wc -l)"
export GIT_BUILD_DIR="$WORKDIR/${PKG_NAME}_${GIT_VERSION}_all"
export GIT_DEB="$WORKDIR/${PKG_NAME}_${GIT_VERSION}_all.deb"
export POOL_PATH="$APT_ROOT/pool/$DEB_VERSION/dev"

echo "--- Building git package"
pip install --prefix="$GIT_BUILD_DIR/usr" --no-cache --no-deps .

find "$GIT_BUILD_DIR" -name "site-packages" | while read dir; do
  base="$(dirname "$dir")"
  mv "$dir" "$base/dist-packages"
done

install -m755 -d "${GIT_BUILD_DIR}/usr/lib/systemd/system"
install -m755 -d "${GIT_BUILD_DIR}/usr/lib/systemd/user"
install -m750 -d "${GIT_BUILD_DIR}/var/lib/platypush"
install -m750 -d "${GIT_BUILD_DIR}/etc/platypush/scripts"

install -m644 "${SRCDIR}/platypush/config/config.yaml" "${GIT_BUILD_DIR}/etc/platypush/config.yaml"
install -m644 "${SRCDIR}/platypush/config/systemd/platypush.service" "${GIT_BUILD_DIR}/usr/lib/systemd/user/platypush.service"
install -m644 "${SRCDIR}/platypush/config/systemd/platypush.service" "${GIT_BUILD_DIR}/usr/lib/systemd/system/platypush.service"
sed -i "${GIT_BUILD_DIR}/usr/lib/systemd/system/platypush.service" -r \
    -e 's/^#\s*Requires=(.*)/Requires=\1/' \
    -e 's/^\[Service\]$/\[Service\]\
User=platypush\
Group=platypush\
WorkingDirectory=\/var\/lib\/platypush\
Environment="PLATYPUSH_CONFIG=\/etc\/platypush\/config.yaml"\
Environment="PLATYPUSH_WORKDIR=\/var\/lib\/platypush"/'

mkdir -p "$GIT_BUILD_DIR/DEBIAN"

cat <<EOF > "$GIT_BUILD_DIR/DEBIAN/control"
Package: $PKG_NAME
Version: $GIT_VERSION
Maintainer: Fabio Manganiello <fabio@platypush.tech>
Depends: $(cat platypush/install/requirements/debian.txt | tr '\n' ',' | sed -re 's/,$//' -e 's/,/, /g')
Architecture: all
Homepage: https://platypush.tech
Description: Universal command executor and automation hub.
EOF

cat <<EOF > "$GIT_BUILD_DIR/DEBIAN/postinst" && chmod +x "$GIT_BUILD_DIR/DEBIAN/postinst"
#!/bin/sh

set -e

if [ "\$1" = "configure" ]; then
  grep -e '^platypush:' /etc/passwd 2>/dev/null || useradd -U -r -s /bin/false -d /var/lib/platypush platypush
  mkdir -p /var/lib/platypush
  chown -R platypush:platypush /var/lib/platypush
  chown -R platypush:platypush /etc/platypush
  if which systemctl; then systemctl daemon-reload; fi
fi
EOF

mkdir -p "$POOL_PATH"
rm -f "$POOL_PATH/"*.deb
dpkg --build "$GIT_BUILD_DIR"

echo "--- Copying $GIT_DEB to $POOL_PATH"
cp "$GIT_DEB" "$POOL_PATH"

# If main/all/Packages doesn't exist, then we should create the first main release
[ $(ls "$APT_ROOT/pool/$DEB_VERSION/main/${PKG_NAME}_${VERSION}-"*"_all.deb" 2>/dev/null | wc -l) -eq 0 ] && export UPDATE_STABLE_PKG=1

export PKGURL="https://apt.platypush.tech/dists/$DEB_VERSION/main/all/Packages"

[ -z "$UPDATE_STABLE_PKG" ] &&
  curl -ILs -o /dev/null -w "%{http_code}" "$PKGURL" |
    grep -e '^4' >/dev/null && export UPDATE_STABLE_PKG=1

# If the published release version differs from the current one, then we should publish a new main release
if [ -z "$UPDATE_STABLE_PKG" ]; then
  RELEASED_VERSION=$(curl -s "$PKGURL" | grep -e '^Version: ' | head -1 | awk '{print $2}' | cut -d- -f 1)
  [ "$RELEASED_VERSION" != "$VERSION" ] && export UPDATE_STABLE_PKG=1
fi

# Proceed and update the main release if the version number has changed
if [ -n "$UPDATE_STABLE_PKG" ]; then
  echo "--- Updating main package"
  mkdir -p "$APT_ROOT/pool/$DEB_VERSION/main"
  cp "$GIT_DEB" "$APT_ROOT/pool/$DEB_VERSION/main/${PKG_NAME}_${VERSION}-1_all.deb"
fi
