#!/bin/bash

PYTHON=python
tests_ret=0

for testcase in tests/test_*.py
do
    $PYTHON -m unittest $testcase
    test_ret=$?

    if [[ $test_ret != 0 ]]; then
        tests_ret=$test_ret
        echo "-------------" >&2
        echo "FAILED: $testcase" >&2
        echo "-------------" >&2
    fi
done

exit $tests_ret


# vim:sw=4:ts=4:et:
