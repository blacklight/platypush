#!/bin/bash

LOGFILE="./docs.log"
STATUS_IMG_PATH="./docs-status.svg"

build_docs() {
    cd ./docs || exit 1
    make html 2>&1 | tee "../$LOGFILE"
    ret=$?
    cd .. || exit 1
    return $?
}

########
# MAIN #
########

build_docs
ret=$?

log_base_path="$(date +/opt/tests/platypush/logs/docs/%Y-%m-%dT%H:%M:%S.%m)"
if [[ $ret == 0 ]]; then
    wget -O "$STATUS_IMG_PATH" https://ci.platypush.tech/docs/passed.svg
    cp "$LOGFILE" "${log_base_path}_PASSED.log"
else
    wget -O "$STATUS_IMG_PATH" https://ci.platypush.tech/docs/failed.svg
    cp "$LOGFILE" "${log_base_path}_FAILED.log"
fi

mv "$STATUS_IMG_PATH" /opt/tests/platypush/logs/docs/
mv "$LOGFILE" /opt/tests/platypush/logs/latest.log
cp -r docs/build/html /opt/repos/platypush/docs/build/
exit $ret
