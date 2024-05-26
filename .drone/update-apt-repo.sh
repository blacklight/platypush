#!/bin/sh

[ -f .skipci ] && exit 0

echo "-- Installing dependencies"
apt update
apt install -y dpkg-dev gpg

echo "-- Creating a new apt root folder"
export TMP_APT_ROOT="/tmp/apt"
cp -r "$APT_ROOT" "$TMP_APT_ROOT"

echo "-- Cleaning up older apt releases"

find "$TMP_APT_ROOT/pool" -mindepth 2 -maxdepth 2 -type d | while read reldir; do
  pkg_to_remove=$(( $(ls "$reldir"/*.deb | wc -l) - 1 ))
  [ $pkg_to_remove -le 0 ] && continue
  ls "$reldir"/*.deb | sort -V | head -n$pkg_to_remove | xargs rm -f
done

echo "-- Updating Packages files"

echo "stable\noldstable" | while read distro; do
  echo "main\ndev" | while read branch; do
    branch_dir="$TMP_APT_ROOT/pool/$distro/$branch"
    echo "Checking pool folder: $branch_dir"
    [ -d "$branch_dir" ] || mkdir -p "$branch_dir"
    dist_dir="$TMP_APT_ROOT/dists/$distro/$branch/all"
    mkdir -p "$dist_dir"
    pkg_file="$dist_dir/Packages"
    dpkg-scanpackages --arch all "$branch_dir" > "$pkg_file"
    sed -i "$pkg_file" -re "s|^Filename: $TMP_APT_ROOT/|Filename: |"
    cat "$pkg_file" | gzip -9 > "$pkg_file.gz"
    echo "Generated Packages file: $pkg_file"
    cat "$pkg_file"
  done
done

echo "-- Updating Release files"

add_hashes() {
  dist_dir=$1
  hash_cmd=$2
  hash_label=$3

  echo "$hash_label:"
  find "$dist_dir" -name 'Packages*' | while read file; do
    basename="$(echo "$file" | sed -r -e "s|^$dist_dir/||")"
    hash="$($hash_cmd "$file" | cut -d" " -f1)"
    size="$(wc -c < $file)"
    echo " $hash $size $basename"
    echo " $hash $size $(echo $basename | sed -re 's|/all/|/binary-i386/|')"
    echo " $hash $size $(echo $basename | sed -re 's|/all/|/binary-amd64/|')"
    echo " $hash $size $(echo $basename | sed -re 's|/all/|/binary-armel/|')"
    echo " $hash $size $(echo $basename | sed -re 's|/all/|/binary-armhf/|')"
    echo " $hash $size $(echo $basename | sed -re 's|/all/|/binary-arm64/|')"
  done
}

echo "stable\noldstable" | while read distro; do
  dist_dir="$TMP_APT_ROOT/dists/$distro"
  components=$(find "$dist_dir" -name Packages | awk -F '/' '{print $(NF-2)}' | uniq | tr '\n' ' ')
  release_file="$dist_dir/Release"

  cat <<EOF > "$release_file"
Origin: Platypush repository
Label: Platypush
Suite: $distro
Codename: $distro
Architectures: i386 amd64 armel armhf arm64
Components: $components
Description: The official APT repository for Platypush
Date: $(date -Ru)
EOF

  add_hashes "$dist_dir" "md5sum" "MD5Sum" >> "$release_file"
  add_hashes "$dist_dir" "sha1sum" "SHA1" >> "$release_file"
  add_hashes "$dist_dir" "sha256sum" "SHA256" >> "$release_file"
done

echo "-- Generating list files"
mkdir -p "$TMP_APT_ROOT/lists"

for distro in stable oldstable; do
  for branch in main dev; do
    echo "deb https://apt.platypush.tech/ $distro $branch" > "$TMP_APT_ROOT/lists/platypush-$distro-$branch.list"
  done
done

echo "-- Updating index file"

cat <<EOF > "$TMP_APT_ROOT/index.txt"
Welcome to the Platypush APT repository!

Project homepage: https://platypush.tech
Source code: https://git.platypush.tech/platypush/platypush
Documentation / API reference: https://docs.platypush.tech

You can use this APT repository to install Platypush on Debian, Ubuntu or any
Debian-based distro.

Steps:

1. Add this repository's PGP key to your apt keyring
====================================================

# wget -q -O \\\
    /etc/apt/trusted.gpg.d/platypush.asc \\\
    https://apt.platypush.tech/pubkey.txt

2. Add the repository to your sources
=====================================

# wget -q -O \\\
    /etc/apt/sources.list.d/platypush.list \\\
    https://apt.platypush.tech/lists/platypush-<deb_version>-<branch>.list

Where:

- deb_version can be:
  - *stable* - current Debian stable version
  - *oldstable* - previous Debian stable version
  - *ubuntu* - latest Ubuntu version

- branch can be either:
  - *main* - latest stable release
  - *dev* a package always in sync with the git version

For example, to install the latest stable tags on Debian stable:

# wget -q -O \\\
    /etc/apt/sources.list.d/platypush.list \\\
    https://apt.platypush.tech/lists/platypush-stable-main.list

3. Update your repos
====================

# apt update

4. Install Platypush
====================

# apt install platypush
EOF

echo "-- Importing and refreshing PGP key"
echo "$PGP_PUBKEY" > "$TMP_APT_ROOT/pubkey.txt"
export PGP_KEYID=$(echo "$PGP_PUBKEY" | gpg --with-colons --import-options show-only --import --fingerprint | grep -e '^fpr:' | head -1 | awk -F ':' '{print $(NF - 1)}')

cat <<EOF | gpg --import --armor
$PGP_PRIVKEY
EOF

echo "-- Signing Release files"

find "$TMP_APT_ROOT/dists" -type f -name Release | while read file; do
  dirname="$(dirname "$file")"
  cat "$file" | gpg -q --default-key "$PGP_KEYID" -abs > "$file.gpg"
  cat "$file" | gpg -q --default-key "$PGP_KEYID" -abs --clearsign > "$dirname/InRelease"
done

echo "-- Updating the apt repo root"
export OLD_APT_ROOT="$REPOS_ROOT/oldapt"
rm -rf "$OLD_APT_ROOT"
mv "$APT_ROOT" "$OLD_APT_ROOT"
mv "$TMP_APT_ROOT" "$APT_ROOT"

chmod -R a+r "$APT_ROOT"
chmod a+x "$APT_ROOT"
