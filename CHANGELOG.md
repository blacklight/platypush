# Changelog

All notable changes to this project will be documented in this file.
Given the high speed of development in the first phase, changes are being
reported only starting from v0.20.2.

## [0.24.0]

### Added

- Added [Wallabag integration](https://git.platypush.tech/platypush/platypush/issues/224).
- Added [Mimic3 TTS integration](https://git.platypush.tech/platypush/platypush/issues/226).
- Added `qos` attribute to `mqtt.publish` and all the plugins derived from `mqtt`.

### Changed

- Replaced PyJWT dependency with the Python-native `rsa` package. This will
  make the installation much lighter, compatible with more systems and less
  dependent on the platform-specific libraries required by `cryptography`.

> **NOTE**: This is a breaking change for those who use the `backend.http` API
> with JWT tokens. The new logic encrypts and encodes the payload in a
> different format, therefore previously generated tokens are no longer
> compatible.

## [0.23.6] - 2022-09-19

### Fixed

- Fixed album_id and list of tracks on `music.tidal.get_album`.

## [0.23.5] - 2022-09-18

### Added

- Added support for web hooks returning their hook method responses back to the
  HTTP client.

- Added [Tidal integration](https://git.platypush.tech/platypush/platypush/pulls/223)

- Added support for [OPML
  subscriptions](https://git.platypush.tech/platypush/platypush/pulls/220) to
  the `rss` plugin.

- Better support for bulk database operations on the `db` plugin.

### Fixed

- Now supporting YAML sections with empty configurations.

## [0.23.4] - 2022-08-28

### Added

- Added `matrix` integration
  ([issue](https://git.platypush.tech/platypush/platypush/issues/2),
  [PR](https://git.platypush.tech/platypush/platypush/pulls/217)).

### Changed

- Removed `clipboard` backend. Enabling the `clipboard` plugin will also enable
  clipboard monitoring, with no need for an additional backend.

## [0.23.3] - 2022-06-01

### Added

- Added `ntfy` integration (see #219).
- Support for a default `config.yaml` if one isn't specified in the default
  locations.

### Changed

- The HTTP server dependencies are now marked as required, since the default
  `config.yaml` will have the HTTP backend enabled by default in order to allow
  the creation of a first user.
- Updated Vue.js frontend dependencies to the latest version.
- Removed bulma from the frontend dependencies, making the frontend much
  lighter and loading times much faster.
- Other UI improvements.

### Fixed

- More reliable cronjobs in case of DST change or any clock changes in general
  (see #217).
- Fixed `--redis-queue` argument.

## [0.23.2] - 2022-03-27

### Added

- Support for asynchronous events over GPIO PINs. It is now possible to specify
  a list of `monitored_pins` in the [`gpio`
  plugin](https://git.platypush.tech/platypush/platypush/-/blob/master/platypush/plugins/gpio/__init__.py)
  configuration. A change in the value on those GPIO PINs (caused by e.g. a
  button, a binary sensor or a probe) will trigger a
  `platypush.message.event.gpio.GPIOEvent` that you can use in your automation
  scripts.

- Simplified script API to interact with platform variables
  (closes [#206](https://git.platypush.tech/platypush/platypush/-/issues/206)).
  You can now read and write stored variables in your Platypush scripts through
  a much more intuitive interface compared to explicitly using the `variable`
  plugin explicitly:

```python
from platypush.context import Variable

# ...

my_var = Variable.get('my_var')
my_var = int(my_var) + 1
Variable.set(my_var=my_var)
```

## [0.23.0] - 2022-03-01

### Added

- Added [Jellyfin integration](https://git.platypush.tech/platypush/platypush/-/issues/208).

### Fixed

- Merged several PRs from `dependabot`.

- Fixed management of the `CN` field in the `calendar.ical` plugin.

## [0.22.10] - 2022-02-07

### Added

- Refactored the `dbus` integration. The plugin and backend have been merged into a
  single plugin component, and the ability to subscribe to custom signals has been
  added.

### Fixed

- Proper support for empty payloads on the integrations that trigger a `SensorDataChangeEvent`.
- Fixed possible infinite recursion on the Pushbullet integration in case of errors where the
  error and close handlers keep calling each other in a loop.

## [0.22.9] - 2022-01-06

### Added

- Added `rss` integration (replaces the cumbersome and deprecated `backend.http.poll`).

### Fixed

- Fixed timezone handling in calendar integrations.
- Fixed handling of ignored directories in the `file.monitor` backend.

## [0.22.8] - 2021-12-13

### Added

- Added support for audio tracks in Plex integration.

### Changed

- Web server uWSGI wrapper changed from `uwsgi` to `gunicorn`.

### Fixed

- Fixed client ID assignment logic in MQTT backends to prevent client ID clashes and reconnections
  (closes #205).
- Updated LTR559 integration to be compatible with the new API.
- Updated Chromecast integration to be compatible with `pychromecast >= 10`.
- Better handling of media errors.

## [0.22.6] - 2021-11-27

### Added

- Added support for converting webpages to markdown in `http.webpage.simplify`
  even if no `outfile` is specified.

### Fixed

- Improved robustness of the ICal calendar parser in case some fields (e.g. `*status`)
  are not defined.

## [0.22.5] - 2021-11-15

### Added

- Added `mastodon` plugin.
- Added `chat.irc` plugin.
- Added `mailgun` plugin.

### Fixed

- Fixed `switchbot.status` method in case of virtual devices.
- Fixed `platypush[alexa]` optional package installation.

## [0.22.4] - 2021-10-19

### Added

- Support for IR virtual devices in Switchbot plugin.
- Added [`google.maps.get_travel_time`](https://docs.platypush.tech/platypush/plugins/google.maps.html#platypush.plugins.google.maps.GoogleMapsPlugin.get_travel_time)
  method (closes #115).
- Support for custom YouTube video/audio formats on media plugins.

### Fixed

- Responses for requests received over an MQTT backend are now delivered to the right topic
  (`<device_base_topic>/responses/<msg_id>`).
- Various fixes on media plugins.

## [0.22.3] - 2021-10-01

### Added

- `gotify` integration (see #198).

## [0.22.2] - 2021-09-25

### Added

- `ngrok` integration (see #196).

## [0.22.1] - 2021-09-22

### Fixed

- `zigbee.mqtt` backend now no longer requires the MQTT backend/plugin to be enabled.

- Fixed bug on empty popcorn API responses.

### Changed

- Created CI Gitlab pipeline to replace the Platypush event-based pre-existing pipeline.

### Removed

- Removed docs references to removed/abstract integrations.

## [0.22.0] - 2021-09-16

### Changed

- Platypush now uses manifest files to describe plugins and backends. Each extension is now
  expected to provide a `manifest.yaml` file in its folder, reporting its package name, pip
  dependencies, required system packages and optional extra installation commands.

- Refactored `platyvenv`, `platydock`, documentation generation and plugin management engine.
  They are now both faster and more robust, since they can rely on the manifest definition to
  operate instead of pydoc strings conventions or `config.yaml` conventions.

- `platyvenv start`  now starts the environment process synchronously and it prints
  stdout/stderr instead of redirecting it to the logs dir (previous behaviour:
  `platyvenv start` used to start the process asynchronously and the logs were stored
  to `~/.local/share/platypush/venv/<env>/logs/<stdout|stderr>.log`).

### Removed

- Removed `Homeseer` integration - it was based on a Python integration that has now been
  pulled out of PyPI and GitHub. A new integration may come in the future if there is enough
  demand for it.

## [0.21.4] - 2021-08-24

### Fixed

- Fixed JWT token generation, since python-jwt >= 2.0 always returns strings (not bytes) upon `jwt.encode`.

## [0.21.3] - 2021-07-28

### Added

- Added `sun` plugin for sunrise/sunset events.

- Added `slack` integration.

## [0.21.2] - 2021-07-20

### Added

- Added `music.spotify` backend to emulate a Spotify Connect receiver through Platypush.

- Added `music.spotify` plugin.

- Added `music.spotify` UI integration.

## [0.21.1] - 2021-06-22

### Added

- Added `switchbot` plugin to interact with Switchbot devices over the cloud API instead of
  directly accessing the device's Bluetooth interface.

- Added `marshmallow` dependency - it will be used from now own to dump and document schemas
  and responses instead of the currently mixed approach with `Response` objects and plain
  dictionaries and lists.

- Support for custom MQTT timeout on all the `zwavejs2mqtt` calls.

- Added generic joystick backend `backend.joystick.jstest` which uses `jstest` from the
  standard `joystick` system package to read the state of joysticks not compatible with
  `python-inputs`.

- Added PWM PCA9685 plugin.

- Added Linux native joystick plugin, ``backend.joystick.linux``, for the cases where
  ``python-inputs`` doesn't work and ``jstest`` is too slow.

### Changed

- `switch.switchbot` plugin renamed to `switchbot.bluetooth` plugin, while the new plugin
  that uses the Switchbot API is simply named `switchbot`.

### Fixed

- More robust reconnection logic on the Pushbullet backend in case of websocket errors.

## [0.21.0] - 2021-05-06

### Added

- Support for custom PopcornTime API mirror/base URL.

- Full support for TV series search.

### Fixed

- Fixed torrent search (now using a different PopcornTime API mirror).

- Migrated SASS engine from `node-sass` (currently deprecated and broken on Node 16) to `sass`.

- Fixed alignment of Z-Wave UI header on Chrome/Webkit.

## [0.20.10] - 2021-04-28

### Fixed

- Fixed zwave/zwavejs2mqtt interoperability.

## [0.20.9] - 2021-04-12

### Added

- Added zwavejs2mqtt integration (see [#186](https://git.platypush.tech/platypush/platypush/-/issues/186).

### Fixed

- Major LINT fixes.

### Removed

- Removed unmaintained integrations: TorrentCast and Booking.com

## [0.20.8] - 2021-04-04

### Added

- Added `<Camera>` dashboard widget.

- Added support for custom dashboard widgets with customized (see https://git.platypush.tech/platypush/platypush/wiki/Backends#creating-custom-widgets).

- Added support for controls on `music.mpd` dashboard widget.

### Fixed

- Fixed zigbee2mqtt backend error in case of messages with empty payload (see [#184](https://git.platypush.tech/platypush/platypush/-/issues/184)).

- Fixed compatibility with all versions of websocket-client - versions >= 0.58.0 pass a `WebSocketApp` object as a first
  argument to the callbacks, as well as versions < 0.54.0 do, but the versions in between don't pass this argument.

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
