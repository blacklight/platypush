# Changelog

All notable changes to this project will be documented in this file.
Given the high speed of development in the first phase, changes are being reported only starting from v0.20.2.

## [Unreleased]

### Added

- Added support for custom dashboard widgets with customized (see https://git.platypush.tech/platypush/platypush/-/wikis/Backends#creating-custom-widgets).

## [0.20.7] - 2021-03-26

### Fixed

- Fixed race condition on `media.vlc.stop` when clearing the VLC instance.

- Fixed dashboard widgets custom classes being propagated both to the container and to the widget content [see #179]

- Fixed compatibility with SQLAlchemy >= 1.4.

## [0.20.6] - 2021-03-16

### Added

- Added `log.http` backend to monitor changes to HTTP log files
  (see [#167](https://git.platypush.tech/platypush/platypush/-/issues/167)).

- Added `file.monitor` backend, which replaces the `inotify` backend
  (see [#172](https://git.platypush.tech/platypush/platypush/-/issues/172)).

### Removed

- Removed legacy `pusher` script and `local` backend.

### Fixed

- Fixed support for Z-Wave switches.

- Fixed possible race condition on VLC stop.

## [0.20.5] - 2021-03-12

### Added

- Added support for a static list of devices to actively scan to the `bluetooth.scanner` backend
  (see [#174](https://git.platypush.tech/platypush/platypush/-/issues/174)).
  
- Added `weather.openweathermap` plugin and backend, which replaces `weather.darksky`, since the
  Darksky API will be completely shut down by the end of 2021.

### Fixed

- Cron expressions should adhere to the UNIX cronjob standard and use the machine local time,
  not UTC, as a reference (closes [#173](https://git.platypush.tech/platypush/platypush/-/issues/173)).
  
- Better management of Z-Wave values types from the UI.

- Disable logging for `ZwaveValueEvent` events - they tend to be very verbose and
  can impact the performance on slower devices. They will still be published to the
  websocket clients though, so you can still debug Z-Wave values issues from the browser
  developer console (enable debug traces).
  
- Added suffix to the `zigbee.mqtt` backend default `client_id` to prevent clashes with
  the default `mqtt` backend `client_id`.

## [0.20.4] - 2021-03-08

### Added

- Added SmartThings integration.
- Support for custom Redis message queue name over the `--redis-queue` argument.

### Fixed

- Refactored tests to use `pytest` instead of `unittest`.
- Some major bug fixes on procedures and hooks context evaluation.

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
