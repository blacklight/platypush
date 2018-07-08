Platypush
=========

[![Build Status](https://travis-ci.org/BlackLight/platypush.svg?branch=master)](https://travis-ci.org/BlackLight/platypush)
[![Documentation Status](https://readthedocs.org/projects/platypush/badge/?version=latest)](https://platypush.readthedocs.io/en/latest/?badge=latest)


Imagine Platypush as some kind of [IFTTT](https://ifttt.com) on steroids - or [Tasker](https://tasker.joaoapps.com/), or [Microsoft Flow](https://flow.microsoft.com), or [PushBullet](https://pushbullet.com) on steroids.
Platypush aims to turn any device in a smart hub that can control things, interact with cloud services and send messages to other devices. It's a general-purpose lightweight platform to process any request and run any logic triggered by custom events.

Imagine the ability of running any task you like, or automate any routine you like, on any of your devices. And the flexibility of executing actions through a cloud service, with the power of running them from your laptop, Raspberry Pi, smart home device or smartphone.

You can use Platypush to do things like:

- Control your smart home lights
- Control your favourite music player
- Interact with your voice assistant
- Get events from your Google or Facebook calendars
- Read data from your sensors and trigger custom events whenever they go above or below some custom thresholds
- Control the motors of your robot
- Send automated emails
- Synchronize the clipboards on your devices
- Control your smart switches
- Implement custom text-to-speech commands
- Build any kind of interaction with your Android device using Tasker
- Play local videos, YouTube videos and torrent links
- Get weather forecast for your location
- Build your own web dashboard with calendar, weather, news and music controls (basically, anything that has a Platypush web widget)
- ...and much more (basically, anything that comes with a [Platypush plugin](https://platypush.readthedocs.io/en/latest/plugins.html))

Imagine the ability of executing all the actions above through messages delivered through:

- A web interface
- Raw HTTP requests
- Web sockets
- [PushBullet](https://pushbullet.com)
- [Kafka](https://kafka.apache.org)
- [Redis](https://redis.io)
- [MQTT](https://mqtt.org)
- ...amd much more (basically, anything that comes with a [Platypush backend](https://platypush.readthedocs.io/en/latest/backends.html))

Imagine the ability of building custom event hooks to automatically trigger any actions:

- When your voice assistant recognizes some text
- When you start playing a new song
- When a new event is added to your calendar
- When a new article is published on your favourite feed
- When the weather conditions change
- When your press a [Flic button](https://flic.io) with a certain pattern
- When you receive a new push on your Pushbullet account
- When your GPS signal enters a certain area
- Whenever a new MIDI event is received (yes, you heard well :) )
- Whenever a sensor sends new data
- At a specific date or time
- ...and so on (basically, anything can send events that can be used to build hooks)

Imagine the ability of running the application, with lots of those bundled features, on any device that can comes with Python (_only compatible with version 3_). Platypush has been designed with performance in mind, it's been heavily tested on slower devices like Raspberry Pis, and it can run the web server features, multiple backends and plugins quite well even on a Raspberry Pi Zero - it's even been tested with some quite impressive performance on an older [Nokia N900](https://en.wikipedia.org/wiki/Nokia_N900), and of course you can run it on any laptop, desktop, server environment. It's been developed mainly with IoT in mind (and some of its features overlap with IoT frameworks like [Mozilla IoT](https://iot.mozilla.com) and [Android Things](https://developer.android.com/things/)), but nothing prevents you from automating any task on any device and environment.

Architecture
------------

The base components are:

* __Messages__: _requests_, _responses_ or _events_. The main difference between a request and an event is that the former specifies an explicit action to be executed through a _plugin_ (and the sender will usually wait for a _response_), while an event only notifies that something happened on a connected data source and can either be ignored or trigger some custom actions specified in the configuration.

* The __Bus__: An internal queue where all the other components exchange messages.

* __Backends__: Components that poll other data sources (a local queue, a remote websocket, a Kafka instance, or even a vocal assistant, a programmable button or a sensor) and post either requests or events on the bus when something happens on the data source. Some of them can have a full-duplex integration with the bus, i.e. post requests and events on the bus as they come and deliver responses from the bus back to the sender (examples: PushBullet, Apache Kafka, sockets), while some are pure data sources that will only post events on the bus (examples: sensors, buttons, vocal assistants).

* __Plugins__: Configurable components which expose _actions_ that can be triggered by requests or events. Examples: smart lights, music controls, YouTube or torrentcast features, text-to-speech, generic shell commands, etc.). They would usually deliver output and errors as responses on the bus.

* __Procedures__: Pre-configured lists of actions that can be triggered by requests or events.

* Event __Hooks__: Pre-configured actions that will be executed when certain events are processed. They include:
    * A _condition_, which can be fuzzly compared against an event. The matching logic will also return a _match score_ if the condition is met. The score is a function of the number of atomic matches (string tokens, scalars, key-values etc.) in the condition that are satisfied by a certain event. If multiple hooks are satisfied by a certain event, the algorithm will only run the ones with the highest score.
    * One or more _actions_ to be executed in case of event match (e.g. "turn on the lights", "send a Messenger message to my s.o.", "turn on the heating", "play the radio" etc.)

Installation
------------

```shell
pip install platypush
```

### Manual Installation

```shell
git clone https://github.com/BlackLight/platypush
cd platypush
python setup.py install
```

Check `requirements.txt` for any extra dependencies you may want to install depending on your configuration. You can also install all the dependencies (may take some time on slow machines) by running `pip install -r requirements.txt`.

After configuring the server, start it by simply running `platypush`.

Check [our wiki](https://github.com/BlackLight/platypush/wiki) for any additional info about [configuration](https://github.com/BlackLight/platypush/wiki/Configuration) together with examples, use the shell interface, or write your own plugins and backend.

