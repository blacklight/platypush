#!/bin/sh

export SKIPCI="$PWD/.skipci"
rm -rf "$SKIPCI"

. .drone/macros/configure-git.sh

cd platypush/backend/http/webapp
if [ $(git log --pretty=oneline $DRONE_COMMIT_AFTER...$DRONE_COMMIT_BEFORE . | wc -l) -eq 0 ]; then
  echo "No UI changes detected, skipping build"
  exit 0
fi


if [ "$(git log --pretty=format:%s HEAD...HEAD~1 | head -1)" == "[Automatic] Updated UI files" ]; then
  echo "UI changes have already been committed, skipping build"
  exit 0
fi

rm -rf dist node_modules
npm install
npm run build

if [ $(git status --porcelain dist | wc -l) -eq 0 ]; then
  echo "No build files have been changed"
  exit 0
fi

# Create a .skipci file to mark the fact that the next steps should be skipped
# (we're going to do another push anyway, so another pipeline will be triggered)
touch "$SKIPCI"

. .drone/macros/configure-ssh.sh
. .drone/macros/configure-gpg.sh

git add dist
git commit dist -S -m "[Automatic] Updated UI files" --no-verify
git remote rm origin
git remote add origin git@git.platypush.tech:platypush/platypush.git
git push -f origin master

# Restore the original git configuration
mv "$TMP_GIT_CONF" "$GIT_CONF"
