#!/bin/sh

[ -z "$PGP_KEY" ] && echo "PGP_KEY is not set" && exit 1
[ -z "$PGP_KEY_ID" ] && echo "PGP_KEY_ID is not set" && exit 1

# Install gpg
if [ -z "$(which gpg)" ]; then
    if [ -n "$(which apt-get)" ]; then
        apt-get update
        apt-get install -y gnupg
    elif [ -n "$(which apk)" ]; then
        apk add --update --no-cache bash gnupg
    elif [ -n "$(which yum)" ]; then
        yum install -y gnupg
    elif [ -n "$(which dnf)" ]; then
        dnf install -y gnupg
    elif [ -n "$(which pacman)" ]; then
        pacman -Sy --noconfirm gnupg
    else
        echo "Could not find a package manager to install gnupg"
        exit 1
    fi
fi

cat <<EOF | gpg --import --armor
$PGP_KEY
EOF

git config commit.gpgsign true
git config user.signingkey "$PGP_KEY_ID"
