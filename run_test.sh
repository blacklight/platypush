#!/bin/bash

PYTHON=python

for testcase in tests/test_*.py
do
    $PYTHON -m unittest $testcase
done

# vim:sw=4:ts=4:et:

