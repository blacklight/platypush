#!/bin/sh

. .drone/macros/configure-git.sh
. .drone/macros/configure-ssh.sh

ssh-keyscan github.com >> ~/.ssh/known_hosts 2>/dev/null

# Clone the repository
git remote add github git@github.com:/BlackLight/platypush.git
git pull --rebase github "$(git branch | head -1 | awk '{print $2}')" || echo "No such branch on Github"

# Push the changes to the GitHub mirror
git push --all -v github
