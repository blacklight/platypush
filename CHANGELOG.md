# Changelog

All notable changes to this project will be documented in this file.
Given the high speed of development in the first phase, changes are being reported only starting from v0.20.2.

## [0.20.3] - 2021-02-28

### Fixed

- Several bug fixes on the VLC plugin, including proper management of stop/end-of-stream, volume set and missing integration requirements in `requirements.txt` and `setup.py`.

## [0.20.2] - 2021-02-27

### Fixed

- More stable ZeroConf backends registration logic in case of partial or missing results.
- Improved and refactored integration tests.

### Added

- Support for passing context variables (${}) from YAML procedures/hooks/crons to Python procedure/hooks/crons.
- New integration test for testing procedures.
