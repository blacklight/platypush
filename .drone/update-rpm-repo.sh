#!/bin/sh

[ -f .skipci ] && exit 0

echo "-- Installing dependencies"
yum install -y \
  createrepo \
  git \
  gpg \
  python \
  python-pip \
  python-setuptools
  rpm-build \
  rpm-sign \
  systemd-rpm-macros \
  wget \
  yum-utils \

echo "-- Copying source directory"
mkdir -p "$WORKDIR"
export SRCDIR="$WORKDIR/src"
cp -r "$PWD" "$SRCDIR"
cd "$SRCDIR"
mkdir -p "$RPM_ROOT"

echo "--- Parsing metadata"
git config --global --add safe.directory $PWD
git pull --rebase origin master --tags
export VERSION=$(python3 setup.py --version)
export RELNUM="$(git log --pretty=oneline HEAD...v$VERSION | wc -l)"
export SPECFILE="$WORKDIR/$PKG_NAME.spec"
export BUILD_DIR="$WORKDIR/build"
export TMP_RPM_ROOT="$WORKDIR/repo"
export SRC_URL="https://git.platypush.tech/platypush/platypush/archive/master.tar.gz"

echo "--- Creating git package spec"

cat <<EOF > $SPECFILE
Summary: Universal command executor and automation hub.
Name: $PKG_NAME-git
Version: $VERSION
Release: $RELNUM
URL: https://platypush.tech
Group: System
License: MIT
Packager: Fabio Manganiello <fabio@platypush.tech>
Source: $SRC_URL
Requires: $(cat platypush/install/requirements/fedora.txt | tr '\n' ' ')
Conflicts: $PKG_NAME
Prefix: %{_prefix}
BuildRoot: %{_tmppath}/%{name}-root
BuildRequires: systemd-rpm-macros
%{?sysusers_requires_compat}

%description
Universal command executor and automation hub.

%install
mkdir -p %{buildroot}/
cp -r "$BUILD_DIR"/* %{buildroot}/
install -p -Dm0644 "${BUILD_DIR}/usr/lib/sysusers.d/platypush.conf" %{buildroot}%{_sysusersdir}/platypush.conf

%pre
%sysusers_create_compat "${BUILD_DIR}/usr/lib/sysusers.d/platypush.conf"

%clean

%files
%defattr(750,platypush,platypush,750)
%dir /etc/platypush
/etc/platypush/*
/usr/bin/*
/usr/lib/python$(python3 --version | awk '{print $2}' | cut -d. -f 1,2)/site-packages/platypush
/usr/lib/python$(python3 --version | awk '{print $2}' | cut -d. -f 1,2)/site-packages/platypush-$VERSION.dist-info
/usr/lib/systemd/system/*
/usr/lib/systemd/user/*
%defattr(750,platypush,platypush,750)
%dir /var/lib/platypush
/var/lib/platypush/*
%{_sysusersdir}/platypush.conf

%changelog
* $(date +'%a %b %d %Y') admin <admin@platypush.tech>
- [Automatic] Release $VERSION-$RELNUM
EOF

echo "--- Building git package"
mkdir -p "$BUILD_DIR"

pip install --prefix="$BUILD_DIR/usr" --no-cache --no-deps .

install -m755 -d "${BUILD_DIR}/usr/lib/systemd/system"
install -m755 -d "${BUILD_DIR}/usr/lib/systemd/user"
install -m755 -d "${BUILD_DIR}/usr/lib/sysusers.d"
install -m750 -d "${BUILD_DIR}/var/lib/platypush"
install -m750 -d "${BUILD_DIR}/etc/platypush/scripts"

install -m644 "${SRCDIR}/platypush/config/config.yaml" "${BUILD_DIR}/etc/platypush/config.yaml"
install -Dm644 "${SRCDIR}/platypush/config/systemd/platypush-sysusers.conf" "${BUILD_DIR}/usr/lib/sysusers.d/platypush.conf"
install -m644 "${SRCDIR}/platypush/config/systemd/platypush.service" "${BUILD_DIR}/usr/lib/systemd/user/platypush.service"
install -m644 "${SRCDIR}/platypush/config/systemd/platypush.service" "${BUILD_DIR}/usr/lib/systemd/system/platypush.service"
sed -i "${BUILD_DIR}/usr/lib/systemd/system/platypush.service" -r \
    -e 's/^#\s*Requires=(.*)/Requires=\1/' \
    -e 's/^\[Service\]$/\[Service\]\
User=platypush\
Group=platypush\
WorkingDirectory=\/var\/lib\/platypush\
Environment="PLATYPUSH_CONFIG=\/etc\/platypush\/config.yaml"\
Environment="PLATYPUSH_WORKDIR=\/var\/lib\/platypush"/'

rpmbuild --target "noarch" -bb "$SPECFILE"

echo "--- Copying the new RPM package"
mkdir -p "$TMP_RPM_ROOT"
cp "$HOME/rpmbuild/RPMS/noarch/$PKG_NAME-git-$VERSION-$RELNUM.noarch.rpm" "$TMP_RPM_ROOT"

echo "--- Checking the latest released stable version"
export LATEST_STABLE_PKG=$(ls -rt "$RPM_ROOT/$PKG_NAME"*.rpm 2>/dev/null | grep -v "$PKG_NAME-git" | tail -1)

if [ -z "$LATEST_STABLE_PKG" ]; then
  # If not stable release is available, then create one
  export UPDATE_STABLE_PKG=1
else
  # Otherwise, create a new release if the reported version on the repo is different
  # from the latest released version.
  export LATEST_STABLE_VERSION=$(basename $LATEST_STABLE_PKG | cut -d- -f 2)
  if [ "$VERSION" != "$LATEST_STABLE_VERSION" ]; then
    export UPDATE_STABLE_PKG=1
  else
    # If the version has remained the same, then simply copy the existing RPM to the
    # new repository directory.
    echo "Copying the existing release $LATEST_STABLE_VERSION to the new repository"
    cp "$LATEST_STABLE_PKG" "$TMP_RPM_ROOT"
  fi
fi

# If a new stable release is required, build another RPM
if [ -n "$UPDATE_STABLE_PKG" ]; then
  export RELNUM=1
  export SRC_URL="https://git.platypush.tech/platypush/platypush/archive/v$VERSION.tar.gz"

  cat <<EOF > $SPECFILE
Summary: Universal command executor and automation hub.
Name: $PKG_NAME
Version: $VERSION
Release: $RELNUM
URL: https://platypush.tech
Group: System
License: MIT
Packager: Fabio Manganiello <fabio@platypush.tech>
Source: $SRC_URL
Requires: $(cat platypush/install/requirements/fedora.txt | tr '\n' ' ')
Conflicts: $PKG_NAME-git
Prefix: %{_prefix}
BuildRoot: %{_tmppath}/%{name}-root
BuildRequires: systemd-rpm-macros
%{?sysusers_requires_compat}

%description
Universal command executor and automation hub.

%install
mkdir -p %{buildroot}/
cp -r "$BUILD_DIR"/* %{buildroot}/
install -p -Dm0644 "${BUILD_DIR}/usr/lib/sysusers.d/platypush.conf" %{buildroot}%{_sysusersdir}/platypush.conf

%pre
%sysusers_create_compat "${BUILD_DIR}/usr/lib/sysusers.d/platypush.conf"

%clean

%files
%defattr(750,platypush,platypush,750)
%dir /etc/platypush
/etc/platypush/*
/usr/bin/*
/usr/lib/python$(python3 --version | awk '{print $2}' | cut -d. -f 1,2)/site-packages/platypush
/usr/lib/python$(python3 --version | awk '{print $2}' | cut -d. -f 1,2)/site-packages/platypush-$VERSION.dist-info
/usr/lib/systemd/system/*
/usr/lib/systemd/user/*
%defattr(750,platypush,platypush,750)
%dir /var/lib/platypush
/var/lib/platypush/*
%{_sysusersdir}/platypush.conf

%changelog
* $(date +'%a %b %d %Y') admin <admin@platypush.tech>
- [Automatic] Release $VERSION-$RELNUM
EOF

  echo "--- Building package for stable release $VERSION"
  rpmbuild --target "noarch" -bb "$SPECFILE"
  cp "$HOME/rpmbuild/RPMS/noarch/$PKG_NAME-$VERSION-$RELNUM.noarch.rpm" "$TMP_RPM_ROOT"
fi

echo "--- Importing the repository keys"
cat <<EOF | gpg --import --armor
$PGP_PRIVKEY
EOF

export PGP_KEYID=$(echo "$PGP_PUBKEY" | gpg --with-colons --import-options show-only --import --fingerprint | grep -e '^fpr:' | head -1 | awk -F ':' '{print $(NF - 1)}')
cat <<EOF > $HOME/.rpmmacros
%signature gpg
%_gpg_name $PGP_KEYID
EOF

echo "--- Signing the new RPM packages"
rpm --addsign "$TMP_RPM_ROOT"/*.rpm

echo "--- Creating a new copy of the RPM repository"
createrepo "$TMP_RPM_ROOT"
gpg --detach-sign --armor "$TMP_RPM_ROOT/repodata/repomd.xml"

cat <<EOF > "$TMP_RPM_ROOT/platypush.repo"
[platypush]
name=Platypush repository
baseurl=https://rpm.platypush.tech
enabled=1
type=rpm
gpgcheck=1
gpgkey=https://rpm.platypush.tech/pubkey.txt
EOF

cat <<EOF > "$TMP_RPM_ROOT/index.txt"
Welcome to the Platypush RPM repository!

Project homepage: https://platypush.tech
Source code: https://git.platypush.tech/platypush/platypush
Documentation / API reference: https://docs.platypush.tech

You can use this RPM repository to install Platypush on Fedora or other
RPM-based distros - as long as they are compatible with the latest Fedora
release.

Steps:

1. Add the repository to your sources
=====================================

$ sudo yum config-manager --add-repo https://rpm.platypush.tech/platypush.repo

2. Install Platypush
====================

$ sudo yum install platypush

Or, if you want to install a version always up-to-date with the git repo:

$ sudo yum install platypush-git
EOF

cat <<EOF > "$TMP_RPM_ROOT/pubkey.txt"
$PGP_PUBKEY
EOF

echo "--- Updating the repository"
export NEW_RPM_ROOT="$REPOS_ROOT/rpm_new"
export OLD_RPM_ROOT="$REPOS_ROOT/rpm_old"
cp -r "$TMP_RPM_ROOT" "$NEW_RPM_ROOT"
rm -rf "$TMP_RPM_ROOT"
mv "$RPM_ROOT" "$OLD_RPM_ROOT"
mv "$NEW_RPM_ROOT" "$RPM_ROOT"
rm -rf "$OLD_RPM_ROOT"
