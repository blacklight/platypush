#!/bin/sh

. .drone/macros/configure-git.sh
. .drone/macros/configure-ssh.sh
. .drone/macros/configure-gpg.sh

# Merge and push to the `stable` branch
git checkout stable
git rebase master
git push -u origin stable
git checkout master

# Restore the original git configuration
mv "$TMP_GIT_CONF" "$GIT_CONF"
