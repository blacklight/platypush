# Changelog

## [1.1.2] - 2024-07-16

- [`core`]: New architecture for the Redis bus - now leveraging pub/sub with a
  connection pool instead of a single-connection queue. It makes the
  application much faster and less prone to Redis deadlocks.

- [`youtube`]:
  [#391](https://git.platypush.tech/platypush/platypush/issues/391): added
  support for:

  - Add/remove playlists (UI)
  - Add to/remove from playlist (UI)
  - Subscribe/unsubscribe from channels (UI)
  - Browse channels and playlists directly in the UI
  - Download media and audio

## [1.1.1] - 2024-06-24

- [`torrent`]: [[#263](https://git.platypush.tech/platypush/platypush/issues/263)], [[#375](https://git.platypush.tech/platypush/platypush/issues/375)],
  [[#407](https://git.platypush.tech/platypush/platypush/issues/407)] and
  [[#408](https://git.platypush.tech/platypush/platypush/issues/408)]: added
  torrents.csv search provider and rewritten torrents UI.

- [[#281](https://git.platypush.tech/platypush/platypush/issues/281)]
  replaced `warnings.warn` with `logging.warning`, as there is no easy and
  reliable way of routing `warnings.warn` to `logging`.

## [1.1.0] - 2024-06-06

- [[#405](https://git.platypush.tech/platypush/platypush/issues/405)] Fixed
  timezone/timestamp rendering issues for `calendar.ical` events.
- [[#403](https://git.platypush.tech/platypush/platypush/issues/403)]
  Included inherited actions in plugins docs.

## [1.0.7] - 2024-06-02

- [[#384](https://git.platypush.tech/platypush/platypush/issues/384)] Added
  `assistant.openai` and `tts.openai` plugins.

## [1.0.6] - 2024-06-01

- 🐛 Bug fix on one of the entities modules that prevented the application from
  loading when `.` is part of `PYTHONPATH`.

## [1.0.5] - 2024-06-01

- A proper solution for the `utcnow()` issue.

It was a bit trickier than expected to solve, but now Platypush uses a
`utcnow()` facade that always returns a UTC datetime in a timezone-aware
representation.

The code should however also handle the case of timestamps stored on the db in
the old format.

## [1.0.4] - 2024-05-31

- Fixed regression introduced by
  [c18768e61fef62924f4c1fac3089ecfb83666dab](https://git.platypush.tech/platypush/platypush/commit/c18768e61fef62924f4c1fac3089ecfb83666dab).
  Python seems to have introduced a breaking change from the version 3.12 -
  `datetime.utcnow()` is not deprecated, but `datetime.UTC`, the suggested
  alternative, isn't available on older versions of Python. Added a workaround
  that makes Platypush compatible with both the implementations.

## [1.0.3] - 2024-05-31

- [[#368](https://git.platypush.tech/platypush/platypush/issues/368)] Added
  Ubuntu packages.

- Fixed bug that didn't get hooks to match events imported through the new
  `platypush.events` symlinked module.

## [1.0.2] - 2024-05-26

- Fixed regression introduced by the support of custom names through the
  `@procedure` decorator.

## [1.0.0] - 2024-05-26

Many, many changes for the first major release of Platypush after so many
years.

- [!3](https://git.platypush.tech/platypush/platypush/milestone/3) All
  backends, except for `http`, `nodered`, `redis` and `tcp`, are gone. Many
  were already deprecated a while ago, but the change now applies to all of
  them. Backends should only be components that actively listen for application
  messages to process, not generic daemon threads for integrations. This had
  been a source of confusion for a long time. Backends and plugins are now
  merged, meaning that you won't need to configure two different sections
  instead of one for many integrations (one for the stateless plugin, and one
  for the background state listener). Please check the
  [documentation](https://docs.platypush.tech) to verify the configuration
  changes required by your integrations. This has been a long process that has
  involved the rewrite of most of the integrations, and many bugs have been
  fixed.

- Improved Docker support - now with a default `docker-compose.yml`, multiple
  Dockerfiles for
  [Alpine](https://git.platypush.tech/platypush/platypush/src/branch/master/platypush/install/docker/alpine.Dockerfile),
  [Debian](https://git.platypush.tech/platypush/platypush/src/branch/master/platypush/install/docker/debian.Dockerfile),
  [Ubuntu](https://git.platypush.tech/platypush/platypush/src/branch/master/platypush/install/docker/ubuntu.Dockerfile)
  and
  [Fedora](https://git.platypush.tech/platypush/platypush/src/branch/master/platypush/install/docker/fedora.Dockerfile)
  base images. Many improvements on the `platydock` and `platyvenv` scripts
  too, with better automated installation processes for optional dependencies.

- Added [official
  packages](https://git.platypush.tech/platypush/platypush#system-package-manager-installation)
  for
  [Debian](https://git.platypush.tech/platypush/platypush#debian-ubuntu)
  and [Fedora](https://git.platypush.tech/platypush/platypush#fedora).

- Added `--device-id`, `--workdir`, `--logsdir`, `--cachedir`, `--main-db`,
  `--redis-host`, `--redis-port` and `--redis-queue` CLI arguments, along the
  `PLATYPUSH_DEVICE_ID`, `PLATYPUSH_WORKDIR`, `PLATYPUSH_LOGSDIR`,
  `PLATYPUSH_CACHEDIR`, `PLATYPUSH_DB`, `PLATYPUSH_REDIS_HOST`,
  `PLATYPUSH_REDIS_PORT` and `PLATYPUSH_REDIS_QUEUE` environment variables.

- Added an _Extensions_ panel to the UI to dynamically:
    - Install new dependencies directly from the Web view.
    - Explore the documentation as well as the supported actions and events for
      each plugin.
    - Get ready-to-paste configuration snippets/templates.

- New, completely rewritten [documentation](https://docs.platypush.tech), which
  now integrates the wiki, dynamically includes plugins configuration snippets
  and dependencies, and adds a global filter bar for the integrations.

- [[#394](https://git.platypush.tech/platypush/platypush/issues/394)] A more
  intuitive way of installing extra dependencies via `pip`. Instead of a static
  list that the user should check inside of `setup.py`, the syntax `pip install
  'platypush[plugin1,plugin2,...]'` is now supported.

- No more need to manually create `__init__.py` in each of the `scripts`
  folders that you want to use to store your custom scripts. Automatic
  discovery of scripts and creation of module files has been implemented. You
  can now just drop a `.py` script with your procedures, hooks or crons in the
  scripts folder and it should be picked up by the application.

- The _Execute_ Web panel now supports procedures too, as well as curl snippets.

- Removed all `Response` objects outside of the root type. They are now all
  replaced by Marshmallow schemas with the structure automatically generated in
  the documentation.

- [`alarm`] [[#340](https://git.platypush.tech/platypush/platypush/issues/340)]
  Rewritten integration. It now includes a powerful UI panel to set up alarms
  with custom procedures too.

- [`assistant.picovoice`]
  [[#304](https://git.platypush.tech/platypush/platypush/issues/304)] New
  all-in-one Picovoice integration that replaces the previous `stt.picovoice.*`
  integrations.

- [`youtube`]
  [[#337](https://git.platypush.tech/platypush/platypush/issues/337)] Full
  rewrite of the plugin. It now supports Piped instances instead of the
  official YouTube API. A new UI has also been designed to explore
  subscriptions, playlists and channels.

- [`weather.*`]
  [[#308](https://git.platypush.tech/platypush/platypush/issues/308)] Removed
  the `weather.darksky` integration (it's now owned by Apple and the API is
  basically dead) and enhanced the `weather.openweathermap` plugin instead.

- [`camera.pi*`] The old `camera.pi` integration based on the deprecated
  `picamera` module has been moved to `camera.pi.legacy`. `camera.pi` is now a
  new plugin which uses the new `picamera2` API (and it's so far only
  compatible with recent versions on the Raspberry Pi OS).

- Dynamically auto-generate plugins documentation in the UI from the RST
  docstrings.

- New design for the configuration panel.

- Better synchronization between processes on threads on application stop -
  greatly reduced the risk of hanging processes on shutdown.

- Migrated all CI/CD pipelines to [Drone
  CI](https://ci-cd.platypush.tech/platypush/platypush).

- Removed `google.fit` integration, as Google has deprecated the API.

- Removed `wiimote` integration: the `cwiid` library hasn't been updated in
  years, it doesn't even work well with Python 3, and I'm not in the mood of
  bringing it back from the dead.

- Removed `stt.deepspeech` integration. That project has been basically
  abandoned by Mozilla, the libraries are very buggy and I don't think it's
  going to see new developments any time soon.

- [[#297](https://git.platypush.tech/platypush/platypush/issues/297)] Removed
  `spotify` backend integration based on Librespot. The project has gone
  through a lot of changes, and I no longer have a Spotify premium account to
  work on a new implementation. Open to contributions if somebody still wants
  it.

## [0.50.3] - 2023-07-22

### Added

- Added [XMPP plugin](https://git.platypush.tech/platypush/platypush/pulls/269).

## [0.50.2] - 2023-06-30

### Fixed

- A fix for the new `get_plugin` supported syntax. `get_plugin` now also
  accepts a plugin class/type as an argument rather than a string, but the
  previous logic didn't properly inspect the parent module.

## [0.50.0] - 2023-06-28

This should actually be a new big major release, but I'm holding on implementing
more features before a 1.0 tag.

### Added

- Migrated many integrations to the new [entities
  framework](https://git.platypush.tech/platypush/platypush/pulls/230).
  This is a very large change to the foundations of the platform. Many plugins
  (and many others will follow) now publish and store their *entities* in a
  standard format, so e.g. all the lights, switches, Bluetooth devices, cameras,
  audio devices, media players and sensors are now supposed to expose the same
  attributes and API regardless of the type of integration. This refactor also
  includes a new default home panel, which includes all the entities detected by
  the registered integrations. Many integrations have already been migrated to
  the new framework. Among them (and many others are on their way):

  - `arduino`
  - `bluetooth`
  - `light.hue`
  - `linode`
  - All the `sensor.*` plugins
  - `serial`
  - `smartthings`
  - `switchbot`
  - `system`
  - `variable`
  - `zigbee.mqtt`
  - `zwave.mqtt`

- Added support for more complex filters on event hooks. Earlier filters could
  only model key-value pair matches. The interface now supports more
  sophisticated filters - among these, structured filters with partial matches
  and relational filters. For example:

```python
from platypush.event.hook import hook
from platypush.message.event.sensor import SensorDataChangeEvent

@hook(SensorDataChangeEvent, data=1):
def hook_1(event):
    """
    Triggered when event.data == 1
    """

@hook(SensorDataChangeEvent, data={'state': 1}):
def hook_2(event):
    """
    Triggered when event.data['state'] == 1
    """

@hook(SensorDataChangeEvent, data={
  'temperature': {'$gt': 25},
  'humidity': {'$le': 15}
}):
def hook_3(event):
    """
    Triggered when event.data['temperature'] > 25 and
    event.data['humidity'] <= 15.
    """
```

The supported relational fields are the same supported by ElasticSearch - `$gt`
for greater than, `$lt` for lesser than, `$ge` for greater or equal, `$ne` for
not equal, etc.

This also means that the previous `SensorDataAboveThresholdEvent` and
`SensorDataBelowThresholdEvent` events are now deprecated, as the new hook API
makes it much easier and flexible to define custom threshold logic on any events
without having to pre-define thresholds in each backend's configuration.

- Added a Progressive WebApp (PWA) framework to the Vue webapp. It is now
  possible to install Platypush as a stand-alone webapp directly from the web
  panel if the panel is served over HTTPS. For now this only improves the user
  experience, performance and it provides a more native-like experience on
  mobile, but in the future the PWA background worker could be used to e.g.
  deliver asynchronous events and notifications to the clients without keeping
  the browser open.

- Added support for application database automatic migrations after an update by
  using Alembic.

### Changed

- Tornado is now used as an HTTP engine by `backend.http`, instead of using
  bare bone Flask with its inefficient Werkzeug server and an optional uwsgi
  that required extra configuration (and an extra external service).

- All the streaming endpoints have been rewritten and adapted to work with
  Tornado. This greatly improves performance, stability and ease of
  configuration, while remaining back-compatible with the previous URL formats.
  As a side note, all the streaming endpoints are now using Redis to stream
  information across multiple worker processes, so make sure that you have a
  version of Redis that supports pub/sub (most of the recent ones should do).

- The `bluetooth` plugin has been completely rewritten, merged with the (now
  deprecated) `backend.bluetooth`. The previously separated low-energy/legacy
  integrations have now been merged too. It now supports much more than passive
  scanning, as it can recognize the information published by most of the device,
  supports both legacy and low-energy connection/disconnection actions, and it
  can detect most of the device classes, services and manufacturers. It also
  supports parsing some standard features (like battery level, temperature,
  state etc.) if they are published according to some convention supported by
  *TheengsGateway*. The `switchbot.bluetooth` integration has now also been
  merged into `bluetooth`.

- The `sound` plugin has been completely rewritten. While it should still be
  largely back-compatible with the previous implementation, you should probably
  go and take a look at the new documentation to get a grasp of the new
  features.

- The `camera.ffmpeg` plugin has received a big rewrite that has improved its
  stability and robustness against several types of cameras. It is now the
  recommended way of interfacing with general-purpose cameras, even for
  PiCameras - the `camera.pi` integration is now largely deprecated, as the old
  PiCamera API is deprecated as well, and `camera.ffmpeg` should now work out of
  the box with a PiCamera if a reasonably recent version of ffmpeg is installed.

- `backend.websocket` has been **removed** and replaced by Tornado asynchronous
   websocket URLs registered on the HTTP backend. The two new routes that
   replace the websocket backend are:

  - `/ws/events`: subscribe to this websocket to receive any asynchronous
    events forwarded by the application.
  - `/ws/requests`: you can send request messages to this endpoints, and the
    responses will be received asynchronously on the same channel.

- The `inspect` plugin has been largely improved.

  - Its performance is now much snappier, as it scans for all the available
    integrations by searching for manifest files instead of scanning each
    single source file. Documentation about specific plugins and actions is
    fetched lazily when requested by the user.
  - It now also caches results by looking at the last modified date of the
    source file, so it won't have to re-scan source files that haven't been
    modified.
  - Its detection of RST constructs has also been improved, so most of the code
    blocks, schemas, return types and references to other objects are now
    rendered in the plugin UI.

- Added `variable.delete` action. The existing `variable.unset` action will now
  only set a variable to null if it exists, while `variable.delete` will
  actually remove it from the database.

- `backend.sensor.distance` and `gpio.sensor.distance` have been removed and
  migrated instead to a new `sensor.hcsr04` plugin, since the existing logic
  actually only applies to HC-SR04-like distance sensors.

- `backend.sensor.dht` and `gpio.sensor.dht` have been removed and
  migrated to a new `sensor.dht` plugin.

- `backend.sensor.accelerometer` and `gpio.sensor.accelerometer` have been
  removed and migrated to a new `sensor.lis3dh` plugin, since the existing
  accelerometer logic only works with these sensors.

- `backend.sensor.motion.pwm3901` and `gpio.sensor.motion.pwm3901` have been
  removed and migrated to a new `sensor.pwm3901` plugin.
  accelerometer logic only works with these sensors.

- `backend.sensor.envirophat` and `gpio.sensor.envirophat` have been removed and
  migrated to a new `sensor.envirophat` plugin.

- `backend.sensor.ltr559` and `gpio.sensor.ltr559` have been removed and
  migrated to a new `sensor.ltr559` plugin.

- `backend.sensor.bme280` and `gpio.sensor.bme280` have been removed and
  migrated to a new `sensor.bme280` plugin.

- `backend.sensor.distance.vl53l1x` and `gpio.sensor.distance.vl53l1x` have been
  removed and migrated to a new `sensor.vl53l1x` plugin.

- `backend.serial` has been removed and merged into the `serial` plugin.

- `backend.switch.wemo` has been removed and merged into the `switch.wemo`
  plugin.

- `backend.switch.tplink` has been removed and merged into the `switch.tplink`
  plugin.

- `backend.zigbee.mqtt` has been removed and merged into the `zigbee.mqtt`
  plugin.

- `backend.zwave.mqtt` has been removed and merged into the `zwave.mqtt` plugin.

### Fixed

- Notable performance improvements for the UI (like -50% on the load time and
  memory usage in some cases). Recursive/reflective Vue components now use
  `shallowRef`, so complex UI models won't have to be fully loaded at page
  start.

- Fixed compatibility with SQLAlchemy 2.

- Migrated the `clipboard` integration from `pyperclip` to `pyclip` (see
  [#240](https://git.platypush.tech/platypush/platypush/issues/240)).
  `pyperclip` is unmaintained and largely broken, and `pyclip` seems to be a
  viable drop-in alternative.

- Better implementation of the UI modals - added close buttons and trigger
  closure when Esc is pressed.

### Removed

- Removed SSL configuration from `backend.http`. Configuring SSL on
  Flask+Tornado is messy, and it won't end up with a good user experience.
  Instead, you should consider using a reverse proxy (e.g. nginx or Apache) if
  you want to make the Platypush web interface available over HTTPS. A sample
  nginx configuration has been added under `examples/nginx`. Note that running
  the web panel over HTTPS is a requirement if you want to leverage the PWA
  features, as a PWA can only be served over HTTPS.

- Removed the Bluetooth file server integration. It is still possible to send
  files over Bluetooth (the feature has now been merged into the `bluetooth`
  plugin, under `bluetooth.send_file`), but all the server features rely on
  features of PyOBEX that are now very broken on recent versions of Python (the
  project itself hasn't been updated in years).

- Removed or deprecated all the `backend.sensor.*` backends. Their logic has now
  been merged into their associated plugins, and the plugins will have the
  ability to run in the background too.

- Removed `backend.sensor.battery`. It has now been merged into the `system`
  plugin.

- Removed `gpio.sensor` plugin. It was never really fully implemented, and it
  was probably impossible to implement with an interface that could work with
  any sensor-like device connected over GPIO.

## [0.24.5] - 2023-02-22

### Added

- Added `hid` plugin to support discoverability and data interaction with
  generic HID devices - like Bluetooth/USB peripherals, joysticks, dongles and
  any other type of devices that supports the HID interface.
  
- Added `timeout` parameter to `websocket.send` to prevent messages sent on a
  non-responsive websocket from getting the websocket loop stuck

### Fixed

- Running the Zeroconf registration logic in another thread in `backend.http`,
  so failures in the Zeroconf logic don't affect the startup of the web server.
  
- (Temporarily) introduced `sqlalchemy < 2.0.0` as a requirement - a PR with a
  migration to the new stable version of SQLAlchemy is in TODO.

## [0.24.4] - 2022-12-20

### Fixed

- Fixed cronjobs potentially being triggered even if it wasn't their slot in
  case of clock synchronization events.

## [0.24.3] - 2022-12-17

### Added

- Added `[-v|--verbose]` command-line option to override the default logging
  configuration and enable debug logging.
- Added `--version` command-line option to print the current version and exit.
- [[#236](https://git.platypush.tech/platypush/platypush/issues/236)] Added
  support for `author` and `tags` attributes on feed entries.

## [0.24.2] - 2022-12-10

### Fixed

- The `main.db` configuration should use the configured `workdir` when no
  values are specified.

- The `zwave.mqtt` is now compatible both with older (i.e. `zwavejs2mqtt`) and
  newer (i.e. `ZwaveJS`) versions of the backend.

## [0.24.1] - 2022-12-08

### Fixed

- Removed a parenthesized context manager that broke compatibility with
  Python &lt; 3.10.

## [0.24.0] - 2022-11-22

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
