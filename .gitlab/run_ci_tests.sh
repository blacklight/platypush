#!/bin/bash

BASE_DIR="$(mktemp -d '/tmp/platypush-ci-tests-XXXXX')"
VENV_DIR="$BASE_DIR/venv"
TEST_LOG="./test.log"
STATUS_IMG_PATH="./status.svg"

cleanup() {
    echo "Cleaning up environment"
    rm -rf "$BASE_DIR"
}

prepare_venv() {
    echo "Preparing virtual environment"
    python -m venv "$VENV_DIR"
    cd "$VENV_DIR" || exit 1
    source ./bin/activate
    cd - || exit 1
}

install_repo() {
    echo "Installing latest version of the repository"
    pip install '.[http]'
}

run_tests() {
    echo "Running tests"
    pytest 2>&1 | tee "$TEST_LOG"
    deactivate

    if grep -e '^FAILED ' "$TEST_LOG"; then
      return 2
    fi

    return 0  # PASSED
}

########
# MAIN #
########

cleanup
prepare_venv
install_repo
run_tests
ret=$?
cleanup

log_base_path="$(date +/opt/tests/platypush/logs/%Y-%m-%dT%H:%M:%S.%m)"
if [[ $ret == 0 ]]; then
    wget -O "$STATUS_IMG_PATH" https://ci.platypush.tech/passed.svg
    cp "$TEST_LOG" "${log_base_path}_PASSED.log"
else
    wget -O "$STATUS_IMG_PATH" https://ci.platypush.tech/failed.svg
    cp "$TEST_LOG" "${log_base_path}_FAILED.log"
fi

mv "$STATUS_IMG_PATH" /opt/tests/platypush/logs/status.svg
mv "$TEST_LOG" /opt/tests/platypush/logs/latest.log
exit $ret
