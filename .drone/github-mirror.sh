#!/bin/sh

. .drone/macros/configure-git.sh
. .drone/macros/configure-ssh.sh

ssh-keyscan github.com >> ~/.ssh/known_hosts 2>/dev/null

# Clone the repository
branch=$(git rev-parse --abbrev-ref HEAD)
if [ -z "${branch}" ]; then
  echo "No branch checked out"
  exit 1
fi

git remote add github git@github.com:/blacklight/platypush.git

if (( "$branch" == "master" )); then
  git pull --rebase github "${branch}" || echo "No such branch on Github"
fi

# Push the changes to the GitHub mirror
git push -f --all -v github
git push --tags -v github
