#!/bin/sh

if [ -z "$SSH_PUBKEY" ] || [ -z "$SSH_PRIVKEY" ]; then
    echo "SSH_PUBKEY and SSH_PRIVKEY environment variables must be set"
    exit 1
fi

# Install ssh
if [ -z "$(which ssh)" ]; then
    if [ -n "$(which apt-get)" ]; then
        apt-get update
        apt-get install -y openssh
    elif [ -n "$(which apk)" ]; then
        apk add --update --no-cache openssh
    elif [ -n "$(which yum)" ]; then
        yum install -y openssh
    elif [ -n "$(which dnf)" ]; then
        dnf install -y openssh
    elif [ -n "$(which pacman)" ]; then
        pacman -Sy --noconfirm openssh
    else
        echo "Could not find a package manager to install openssh"
        exit 1
    fi
fi

mkdir -p ~/.ssh
echo $SSH_PUBKEY > ~/.ssh/id_rsa.pub

cat <<EOF > ~/.ssh/id_rsa
$SSH_PRIVKEY
EOF

chmod 0600 ~/.ssh/id_rsa
ssh-keyscan git.platypush.tech >> ~/.ssh/known_hosts 2>/dev/null
