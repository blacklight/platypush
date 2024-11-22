#!/bin/sh

export SKIPCI="$PWD/.skipci"
export CACHEFILE="$PWD/platypush/components.json.gz"

[ -f "$SKIPCI" ] && exit 0

# Backup the original git configuration before changing attributes
export GIT_CONF="$PWD/.git/config"
export TMP_GIT_CONF="/tmp/git.config.orig"
cp "$GIT_CONF" "$TMP_GIT_CONF"

. .drone/macros/configure-git.sh

# Only regenerate the components cache if either the plugins, backends,
# events or schemas folders have some changes (excluding the webapp files).
if [ -z "$(git log --pretty=oneline $DRONE_COMMIT_AFTER...$DRONE_COMMIT_BEFORE -- platypush/backend platypush/plugins platypush/schemas platypush/message/event ':(exclude)platypush/backend/http/webapp')" ]; then
  echo 'No changes to the components file'
  exit 0
fi

. .drone/macros/configure-ssh.sh
. .drone/macros/configure-gpg.sh

echo 'Updating components cache'
apk add --update --no-cache $(cat platypush/install/requirements/alpine.txt)
pip install . --break-system-packages

python - <<EOF
from platypush import get_plugin

get_plugin('inspect').refresh_cache(force=True)
EOF

# Create a .skipci file to mark the fact that the next steps should be skipped
# (we're going to do another push anyway, so another pipeline will be triggered)
touch "$SKIPCI"

git add "$CACHEFILE"
git commit "$CACHEFILE" -S -m "[Automatic] Updated components cache" --no-verify
git remote rm origin
git remote add origin git@git.platypush.tech:platypush/platypush.git
git push -f origin master

# Restore the original git configuration
mv "$TMP_GIT_CONF" "$GIT_CONF"
